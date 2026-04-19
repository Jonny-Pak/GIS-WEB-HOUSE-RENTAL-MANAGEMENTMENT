import json
import hashlib
import re
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


CITY_ALIASES = [
    'Thành phố Hồ Chí Minh',
    'TP Hồ Chí Minh',
    'TP.HCM',
    'Ho Chi Minh City',
    'Sai Gon',
]

HCMC_BOUNDS = {
    'min_lat': 10.3,
    'max_lat': 11.3,
    'min_lng': 106.2,
    'max_lng': 107.1,
}


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
        (r'\bH\.\s*([A-Za-zÀ-ỹ0-9]+)\b', r'Huyện \1'),
        (r'\bX\.\s*([A-Za-zÀ-ỹ0-9]+)\b', r'Xã \1'),
    ]

    for pattern, replacement in rules:
        variants.add(re.sub(pattern, replacement, base, flags=re.IGNORECASE))

    variants.add(_ascii_fold(base))
    return [item for item in variants if item.strip()]


def _normalize_address_segments(address: str) -> list[str]:
    parts = [re.sub(r'\s+', ' ', part).strip() for part in (address or '').split(',')]
    parts = [part for part in parts if part]

    deduped = []
    seen = set()
    for part in parts:
        key = _ascii_fold(part).lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(part)

    return deduped


def _is_admin_segment(segment: str) -> bool:
    token = _ascii_fold(segment).lower()
    return any(
        marker in token
        for marker in [
            'phuong',
            'xa',
            'thi tran',
            'quan',
            'huyen',
            'thanh pho',
            'tp ',
            'tinh',
        ]
    )


def _pick_best_ward_segment(segments: list[str]) -> str:
    ward_segments = [
        seg for seg in segments
        if any(marker in _ascii_fold(seg).lower() for marker in ['phuong', 'xa', 'thi tran'])
    ]
    if not ward_segments:
        return ''

    numeric_ward = [seg for seg in ward_segments if re.search(r'\d+', seg)]
    if numeric_ward:
        return numeric_ward[0]

    return ward_segments[0]


def _build_priority_candidates(address: str) -> list[str]:
    segments = _normalize_address_segments(_clean_google_maps_address(address))
    if not segments:
        return []

    street_segments = [seg for seg in segments if not _is_admin_segment(seg)]
    street = street_segments[0] if street_segments else segments[0]
    ward = _pick_best_ward_segment(segments)

    city_variants = ['Thành phố Hồ Chí Minh', 'Ho Chi Minh City']
    country_variants = ['Việt Nam', 'Vietnam']

    candidates = []
    for city in city_variants:
        for country in country_variants:
            if ward:
                candidates.append(f'{street}, {ward}, {city}, {country}')
            candidates.append(f'{street}, {city}, {country}')

    return candidates


def _clean_google_maps_address(address: str) -> str:
    text = re.sub(r'\s+', ' ', (address or '').strip())
    if not text:
        return ''

    # Remove common country tails from copy-pasted map addresses.
    text = re.sub(r',?\s*(Việt\s*Nam|Viet\s*Nam|Vietnam)\s*$', '', text, flags=re.IGNORECASE)

    # Keep the input compact and avoid duplicated separators.
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'(,\s*){2,}', ', ', text)
    return text.strip(' ,')


def _build_shortened_address_variants(address: str) -> list[str]:
    cleaned = _clean_google_maps_address(address)
    parts = _normalize_address_segments(cleaned)
    if not parts:
        return []

    variants = []

    # Start with concise variants first to improve hit-rate under limited API calls.
    if len(parts) >= 2:
        variants.append(', '.join(parts[:2]))
    if len(parts) >= 3:
        variants.append(', '.join(parts[:3]))
    if len(parts) >= 4:
        variants.append(', '.join(parts[:4]))

    # Full text later.
    variants.append(', '.join(parts))

    # Progressively simplify long administrative tails.
    for keep in range(max(len(parts) - 1, 1), 0, -1):
        candidate = ', '.join(parts[:keep]).strip()
        if candidate:
            variants.append(candidate)

    # Also try a compact variant for noisy inputs.
    compact = ' '.join(parts[: min(3, len(parts))]).strip()
    if compact:
        variants.append(compact)

    deduped = []
    seen = set()
    for item in variants:
        key = _ascii_fold(item).lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _build_candidates(address: str) -> list[str]:
    cleaned_address = _clean_google_maps_address(address)
    address_variants = _expand_vn_abbreviations(cleaned_address)
    for short_variant in _build_shortened_address_variants(address):
        address_variants.extend(_expand_vn_abbreviations(short_variant))

    candidates = _build_priority_candidates(cleaned_address)

    for address_variant in address_variants:
        candidates.append(address_variant)
        candidates.append(f'{address_variant}, Thành phố Hồ Chí Minh, Việt Nam')
        candidates.append(f'{address_variant}, Ho Chi Minh City, Vietnam')
        candidates.append(f'{address_variant}, Việt Nam')
        candidates.append(f'{address_variant}, Vietnam')

    candidates.extend([_ascii_fold(item) for item in candidates if item])

    deduplicated = []
    seen = set()
    for candidate in candidates:
        key = candidate.lower()
        if candidate and key not in seen:
            seen.add(key)
            deduplicated.append(candidate)
    return deduplicated


def _get_nominatim_endpoints() -> list[str]:
    raw = (getattr(settings, 'GEOCODING_NOMINATIM_ENDPOINTS', '') or '').strip()
    if raw:
        endpoints = [item.strip().rstrip('/') for item in raw.split(',') if item.strip()]
        if endpoints:
            return endpoints

    return [
        'https://nominatim.openstreetmap.org',
        'https://nominatim.openstreetmap.fr',
    ]


def _build_cache_key(address: str) -> str:
    fingerprint = _ascii_fold(f'{address}').lower()
    digest = hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()
    return f'geocode:hcm:{digest}'


def _tokenize(text: str) -> list[str]:
    raw = _ascii_fold(text or '').lower()
    parts = re.split(r'[^a-z0-9]+', raw)
    return [item for item in parts if len(item) >= 2]


def _build_street_tokens(address: str) -> list[str]:
    segments = _normalize_address_segments(_clean_google_maps_address(address))
    if not segments:
        return []
    street_segments = [seg for seg in segments if not _is_admin_segment(seg)]
    target = street_segments[0] if street_segments else segments[0]
    return _tokenize(target)


def _score_nominatim_result(result: dict, address: str) -> float:
    display_name = _ascii_fold(result.get('display_name', '')).lower()
    address_obj = result.get('address') or {}
    address_text = _ascii_fold(' '.join(str(v) for v in address_obj.values())).lower()
    merged = f'{display_name} {address_text}'

    score = 0.0

    for token in _build_street_tokens(address)[:6]:
        if token in merged:
            score += 0.9

    try:
        importance = float(result.get('importance', 0.0) or 0.0)
    except (TypeError, ValueError):
        importance = 0.0
    score += min(importance * 2.0, 1.5)

    category = str(result.get('class', '')).lower()
    item_type = str(result.get('type', '')).lower()
    if category in {'building', 'place'} or item_type in {'house', 'residential', 'apartments'}:
        score += 0.6

    return score


def _extract_coords_from_text(text: str) -> tuple[float | None, float | None]:
    payload = (text or '').strip()
    if not payload:
        return None, None

    # Support simple pasted forms such as "10.123, 106.456".
    direct = re.search(r'(-?\d{1,2}\.\d+)\s*[,;\s]\s*(-?\d{1,3}\.\d+)', payload)
    if direct:
        try:
            lat = float(direct.group(1))
            lng = float(direct.group(2))
            if _is_in_hcmc_bounds(lat, lng):
                return lat, lng
        except (TypeError, ValueError):
            pass

    # Support Google Maps links containing "@lat,lng".
    link_match = re.search(r'@(-?\d{1,2}\.\d+),(-?\d{1,3}\.\d+)', payload)
    if link_match:
        try:
            lat = float(link_match.group(1))
            lng = float(link_match.group(2))
            if _is_in_hcmc_bounds(lat, lng):
                return lat, lng
        except (TypeError, ValueError):
            pass

    return None, None


def _is_in_hcmc_bounds(lat: float, lng: float) -> bool:
    return (
        HCMC_BOUNDS['min_lat'] <= lat <= HCMC_BOUNDS['max_lat']
        and HCMC_BOUNDS['min_lng'] <= lng <= HCMC_BOUNDS['max_lng']
    )


def _geocode_nominatim(query: str, address: str) -> tuple[float | None, float | None, str]:
    timeout = int(getattr(settings, 'GEOCODING_TIMEOUT', 6))
    import uuid
    dynamic_suffix = str(uuid.uuid4())[:8]
    user_agent = getattr(settings, 'GEOCODING_USER_AGENT', f'viet-house-rental/{dynamic_suffix} (admin@example.com)')
    had_rate_limit = False

    for endpoint in _get_nominatim_endpoints():
        params = {
            'q': query,
            'format': 'jsonv2',
            'limit': '5',
            'addressdetails': '1',
            'countrycodes': 'vn',
            'dedupe': '1',
        }

        # Apply HCMC Viewbox to bias search
        center_lat, center_lng = (10.762622, 106.660172)
        delta = 0.25
        min_lng = center_lng - delta
        min_lat = center_lat - delta
        max_lng = center_lng + delta
        max_lat = center_lat + delta
        params['viewbox'] = f'{min_lng},{min_lat},{max_lng},{max_lat}'

        url = f"{endpoint}/search?{urlencode(params)}"

        try:
            request = Request(url, headers={'User-Agent': user_agent})
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode('utf-8'))
        except HTTPError as error:
            if getattr(error, 'code', None) == 429:
                had_rate_limit = True
                continue
            continue
        except (URLError, TimeoutError, ValueError, KeyError):
            continue

        if not payload:
            continue

        best_result = None
        best_score = -1.0
        for item in payload:
            try:
                lat = float(item['lat'])
                lng = float(item['lon'])
            except (TypeError, ValueError, KeyError):
                continue

            if not _is_in_hcmc_bounds(lat, lng):
                continue

            score = _score_nominatim_result(item, address)
            if score > best_score:
                best_score = score
                best_result = (lat, lng)

        # Removed 4.2 constraint because we don't naturally score District keywords (+4.0) anymore!
        # Now relying on bounding box and street segment match.
        if best_result and best_score >= 0.5:
            return best_result[0], best_result[1], 'geocoded_nominatim'

    if had_rate_limit:
        return None, None, 'nominatim_rate_limited'

    return None, None, 'no_result'


def resolve_house_coordinates(
    address: str, 
    user_lat: float | None = None, 
    user_lng: float | None = None
) -> tuple[float | None, float | None, str]:
    if user_lat is not None and user_lng is not None and _is_in_hcmc_bounds(user_lat, user_lng):
        return user_lat, user_lng, 'gps_location'

    cache_key = _build_cache_key(address)
    cached_value = cache.get(cache_key)
    if cached_value:
        return cached_value[0], cached_value[1], 'cached'

    parsed_lat, parsed_lng = _extract_coords_from_text(address)
    if parsed_lat is not None and parsed_lng is not None:
        result = (parsed_lat, parsed_lng, 'parsed_from_input')
        cache.set(cache_key, (parsed_lat, parsed_lng), int(getattr(settings, 'GEOCODING_CACHE_TIMEOUT', 86400)))
        return result

    candidates = _build_candidates(address)

    nominatim_candidates = 3
    nominatim_attempted = 0
    saw_rate_limit = False

    cleaned_address = _clean_google_maps_address(address)
    minimal_search = f"{cleaned_address}, Thành phố Hồ Chí Minh, Việt Nam"
    
    prioritized_candidates = [
        minimal_search,
        cleaned_address
    ]

    for candidate in prioritized_candidates:
        if nominatim_attempted >= nominatim_candidates:
            break
        try:
            import time
            if nominatim_attempted > 0:
                time.sleep(1.2)
            
            nominatim_attempted += 1
            lat, lng, state = _geocode_nominatim(
                query=candidate,
                address=address,
            )
            if lat is not None and lng is not None:
                cache.set(cache_key, (lat, lng), int(getattr(settings, 'GEOCODING_CACHE_TIMEOUT', 86400)))
                return lat, lng, state
            if state == 'nominatim_rate_limited':
                saw_rate_limit = True
                break
        except (ValueError, KeyError, TimeoutError, HTTPError, URLError):
            continue

    if saw_rate_limit:
        return None, None, 'nominatim_rate_limited'

    # Fallback to center of HCMC
    return 10.762622, 106.660172, 'hcmc_center_fallback'

def reverse_geocode_nominatim(lat: float, lng: float) -> str | None:
    timeout = int(getattr(settings, 'GEOCODING_TIMEOUT', 6))
    import uuid
    dynamic_suffix = str(uuid.uuid4())[:8]
    user_agent = getattr(settings, 'GEOCODING_USER_AGENT', f'viet-house-rental-reverse/{dynamic_suffix} (admin@example.com)')

    attempted = 0
    for endpoint in _get_nominatim_endpoints():
        params = {
            'lat': str(lat),
            'lon': str(lng),
            'format': 'jsonv2',
            'addressdetails': '1',
            'zoom': '18'
        }
        url = f"{endpoint}/reverse?{urlencode(params)}"
        
        try:
            import time
            if attempted > 0:
                time.sleep(1.2)  # Respect OSM limits when retrying
            attempted += 1
            request = Request(url, headers={'User-Agent': user_agent})
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode('utf-8'))
                
            if payload and 'address' in payload:
                addr = payload['address']
                parts = []
                
                if 'house_number' in addr:
                    parts.append(addr['house_number'])
                
                if 'road' in addr:
                    parts.append(addr['road'])
                elif 'pedestrian' in addr:
                    parts.append(addr['pedestrian'])
                elif 'path' in addr:
                    parts.append(addr['path'])
                    
                ward = addr.get('suburb') or addr.get('quarter') or addr.get('neighbourhood')
                if ward:
                    parts.append(ward)
                    
                if parts:
                    return ', '.join(parts)
                elif 'display_name' in payload:
                    name = payload['display_name'].split(',')[0]
                    return name
        except Exception:
            continue
            
    return None
