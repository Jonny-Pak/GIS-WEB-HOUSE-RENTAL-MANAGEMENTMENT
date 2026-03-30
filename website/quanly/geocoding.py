import json
import re
import unicodedata
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.conf import settings

DISTRICT_CENTER_COORDS = {
    'q1': (10.7769, 106.7009),
    'q2': (10.7872, 106.7498),
    'q3': (10.7829, 106.6871),
    'q4': (10.7577, 106.7015),
    'q5': (10.7540, 106.6670),
    'q6': (10.7460, 106.6350),
    'q7': (10.7298, 106.7219),
    'q8': (10.7247, 106.6286),
    'q9': (10.8427, 106.8287),
    'q10': (10.7731, 106.6676),
    'q11': (10.7633, 106.6504),
    'q12': (10.8617, 106.7610),
    'qbt': (10.8036, 106.7077),
    'qtb': (10.8039, 106.6522),
    'qtp': (10.7908, 106.6282),
    'qp': (10.8008, 106.6798),
    'qgv': (10.8388, 106.6653),
    'qbtan': (10.7653, 106.6006),
    'td': (10.8413, 106.8099),
    'hbc': (10.6953, 106.5938),
    'hhm': (10.8890, 106.5955),
    'hcc': (10.9733, 106.4936),
    'hnb': (10.6795, 106.7327),
    'hcg': (10.4114, 106.9547),
}

# Hỗ trợ địa chỉ cũ/mới phổ biến để tăng tỉ lệ geocode đúng.
DISTRICT_ALIASES = {
    'td': ['Thành phố Thủ Đức', 'TP Thủ Đức', 'Quận 2', 'Quận 9'],
    'qbt': ['Quận Bình Thạnh', 'Bình Thạnh'],
    'qtp': ['Quận Tân Phú', 'Tân Phú'],
    'qtb': ['Quận Tân Bình', 'Tân Bình'],
}

CITY_ALIASES = [
    'Thành phố Hồ Chí Minh',
    'TP Hồ Chí Minh',
    'TP.HCM',
    'Ho Chi Minh City',
    'Sai Gon',
]


def _ascii_fold(text: str) -> str:
    normalized = unicodedata.normalize('NFD', text or '')
    without_marks = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
    return re.sub(r'\s+', ' ', without_marks).strip()


def _expand_vn_abbreviations(address: str) -> list[str]:
    base = re.sub(r'\s+', ' ', (address or '').strip())
    if not base:
        return []

    variants = {base}
    rules = [
        (r'\bP\.?\s*(\d+)\b', r'Phường \1'),
        (r'\bQ\.?\s*(\d+)\b', r'Quận \1'),
        (r'\bTP\.?\s*HCM\b', 'Thành phố Hồ Chí Minh'),
        (r'\bTP\.?\s*Ho\s*Chi\s*Minh\b', 'Thành phố Hồ Chí Minh'),
        (r'\bKP\.?\b', 'Khu phố'),
        (r'\bTT\.?\b', 'Thị trấn'),
        (r'\bH\.?\s*([A-Za-zÀ-ỹ0-9]+)\b', r'Huyện \1'),
        (r'\bX\.?\s*([A-Za-zÀ-ỹ0-9]+)\b', r'Xã \1'),
    ]

    for pattern, replacement in rules:
        variants.add(re.sub(pattern, replacement, base, flags=re.IGNORECASE))

    # Thêm bản viết không dấu để geocoder bắt tốt hơn khi người dùng nhập không dấu.
    variants.add(_ascii_fold(base))
    return [item for item in variants if item.strip()]


def _build_candidates(address: str, district_code: str, district_display: str) -> list[str]:
    address_variants = _expand_vn_abbreviations(address)
    district_names = [district_display] if district_display else []
    district_names.extend(DISTRICT_ALIASES.get(district_code, []))

    candidates = []
    for address_variant in address_variants:
        for district_name in district_names:
            for city_name in CITY_ALIASES:
                candidates.append(f'{address_variant}, {district_name}, {city_name}, Việt Nam')
                candidates.append(f'{address_variant}, {district_name}, {city_name}, Vietnam')

    # Thử thêm phiên bản bỏ dấu để hỗ trợ các bộ geocoder khó tính.
    candidates.extend([_ascii_fold(item) for item in candidates if item])

    deduplicated = []
    seen = set()
    for c in candidates:
        key = c.lower()
        if c and key not in seen:
            seen.add(key)
            deduplicated.append(c)
    return deduplicated


def _geocode_nominatim(query: str) -> tuple[float | None, float | None]:
    timeout = int(getattr(settings, 'GEOCODING_TIMEOUT', 6))
    user_agent = getattr(settings, 'GEOCODING_USER_AGENT', 'ltgis-house-rental/1.0')
    url = (
        'https://nominatim.openstreetmap.org/search'
        f'?q={quote(query)}&format=jsonv2&limit=1&addressdetails=1'
    )

    request = Request(url, headers={'User-Agent': user_agent})
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode('utf-8'))

    if not payload:
        return None, None

    lat = float(payload[0]['lat'])
    lng = float(payload[0]['lon'])
    return lat, lng


def resolve_house_coordinates(address: str, district_code: str, district_display: str) -> tuple[float | None, float | None, str]:
    candidates = _build_candidates(address, district_code, district_display)

    for candidate in candidates[:10]:
        try:
            lat, lng = _geocode_nominatim(candidate)
            if lat is not None and lng is not None:
                return lat, lng, 'geocoded'
        except (ValueError, KeyError, TimeoutError, HTTPError, URLError):
            continue

    # Không dùng fallback - trả về None để admin nhập tay
    return None, None, 'failed'


def resolve_search_address(query: str) -> tuple[float | None, float | None, str]:
    """
    Geocode địa chỉ tự do cho chức năng tìm kiếm bản đồ.
    Trả về (lat, lng, status) với status thuộc {'geocoded', 'failed'}.
    """
    cleaned = re.sub(r'\s+', ' ', (query or '').strip())
    if not cleaned:
        return None, None, 'failed'

    candidates = [cleaned]
    if 'hồ chí minh' not in cleaned.lower() and 'ho chi minh' not in cleaned.lower() and 'hcm' not in cleaned.lower():
        candidates.append(f'{cleaned}, Thành phố Hồ Chí Minh, Việt Nam')
        candidates.append(f'{cleaned}, Ho Chi Minh City, Vietnam')

    # Thử thêm biến thể không dấu để tăng tỉ lệ geocode thành công.
    candidates.append(_ascii_fold(cleaned))

    seen = set()
    for candidate in candidates:
        key = candidate.lower()
        if key in seen:
            continue
        seen.add(key)

        try:
            lat, lng = _geocode_nominatim(candidate)
            if lat is not None and lng is not None:
                return lat, lng, 'geocoded'
        except (ValueError, KeyError, TimeoutError, HTTPError, URLError):
            continue

    return None, None, 'failed'
