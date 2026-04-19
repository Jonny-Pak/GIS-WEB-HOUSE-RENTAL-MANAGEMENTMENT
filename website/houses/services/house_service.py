import math
from shapely.geometry import Point, Polygon
from houses.models import Furniture, House, HouseFurnitureItem, HouseImage
from houses.services.geocoding import resolve_house_coordinates


# ==================== GEO SERVICES ====================

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa 2 điểm tọa độ bằng công thức Haversine (đơn vị: km)
    """
    R = 6371.0 # Bán kính Trái đất (km)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def get_nearby_houses_qs(user_lat, user_long, radius_km=5):
    """
    Lọc danh sách nhà xung quanh dựa trên tính toán khoảng cách Haversine
    Trả về: List các Object House (không phải QuerySet thuần vì đã qua xử lý list comprehension)
    """
    houses = House.objects.filter(status='available', lat__isnull=False, lng__isnull=False)
    
    nearby_houses = []
    for house in houses:
        dist = calculate_distance(user_lat, user_long, house.lat, house.lng)
        if dist <= radius_km:
            house.distance = dist # Gắn tạm biến distance vào object để Serializer đọc
            nearby_houses.append(house)
            
    # Sắp xếp theo khoảng cách gần nhất
    nearby_houses.sort(key=lambda x: x.distance)
    return nearby_houses

def get_houses_in_polygon_qs(polygon_coords):
    """
    Lấy danh sách nhà nằm trong đa giác được vẽ ra, sử dụng Shapely (Polygon.contains)
    """
    if len(polygon_coords) < 3:
        return []
        
    # Hỗ trợ 2 chuẩn gửi lên: Array object [{"lat": 10, "lng": 106}] hoặc Array lồng nhau [[10, 106]]
    poly_coords = []
    for pt in polygon_coords:
        if isinstance(pt, dict):
            # Lấy lng trước, lat sau (chuẩn x, y của Shapely)
            poly_coords.append((float(pt.get('lng', 0)), float(pt.get('lat', 0))))
        elif isinstance(pt, list) and len(pt) >= 2:
            # pt[0] là lat, pt[1] là lng (theo như hình của bạn)
            poly_coords.append((float(pt[1]), float(pt[0])))

    # Khởi tạo Shapely Polygon
    shapely_poly = Polygon(poly_coords)

    houses = House.objects.filter(status='available', lat__isnull=False, lng__isnull=False)
    
    houses_in_poly = []
    for house in houses:
        house_point = Point(house.lng, house.lat)
        # Sử dụng hàm contains() của shapely để kiểm tra nhà có nằm trong đa giác không
        if shapely_poly.contains(house_point):
            houses_in_poly.append(house)
            
    return houses_in_poly


def _parse_furniture_from_request(request):
    selected_ids = request.POST.getlist('furniture_ids')
    normalized = []
    seen = set()

    for item in selected_ids:
        try:
            furniture_id = int(item)
        except (TypeError, ValueError):
            continue

        if furniture_id in seen:
            continue

        seen.add(furniture_id)
        quantity_raw = (request.POST.get(f'quantity_{furniture_id}', '1') or '').strip()
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            quantity = 1

        normalized.append((furniture_id, quantity))

    return normalized


def build_furniture_choices(request=None, house=None):
    furnitures = Furniture.objects.order_by('name')
    selected_quantities = {}

    if house is not None:
        selected_quantities = {
            item.furniture_id: item.quantity
            for item in house.furniture_items.all()
        }

    if request is not None and request.method == 'POST':
        selected_quantities = {
            furniture_id: quantity
            for furniture_id, quantity in _parse_furniture_from_request(request)
        }

    return [
        {
            'id': furniture.id,
            'name': furniture.name,
            'selected': furniture.id in selected_quantities,
            'quantity': selected_quantities.get(furniture.id, 1),
        }
        for furniture in furnitures
    ]


def save_house_furniture(house, request):
    selected_pairs = _parse_furniture_from_request(request)
    selected_ids = [furniture_id for furniture_id, _ in selected_pairs]

    furniture_map = {
        furniture.id: furniture
        for furniture in Furniture.objects.filter(id__in=selected_ids)
    }

    HouseFurnitureItem.objects.filter(house=house).delete()
    house.furniture.clear()

    items_to_create = []
    valid_ids = []
    for furniture_id, quantity in selected_pairs:
        if furniture_id not in furniture_map:
            continue
        valid_ids.append(furniture_id)
        items_to_create.append(
            HouseFurnitureItem(
                house=house,
                furniture=furniture_map[furniture_id],
                quantity=quantity,
            )
        )

    try:
        HouseFurnitureItem.objects.filter(house=house).delete()
        house.furniture.clear()

        if items_to_create:
            HouseFurnitureItem.objects.bulk_create(items_to_create)
        house.furniture.set(valid_ids)
    except Exception:
        # Fall back to basic many-to-many if detail table is unavailable.
        house.furniture.set(valid_ids)


def _resolve_house_location(house):
    return resolve_house_coordinates(
        address=house.address or '',
    )


def _parse_manual_coordinates(request):
    if request is None:
        return None, None

    lat_raw = (request.POST.get('manual_lat') or '').strip().replace(',', '.')
    lng_raw = (request.POST.get('manual_lng') or '').strip().replace(',', '.')
    if not lat_raw or not lng_raw:
        return None, None

    try:
        lat = float(lat_raw)
        lng = float(lng_raw)
    except (TypeError, ValueError):
        return None, None

    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None, None

    return lat, lng


# ==================== LANDLORD SERVICES ====================

def create_house(form, owner, images=None, request=None):
    """
    Tạo mới một bài đăng nhà.
    - Gán chủ nhà (owner)
    - Thiết lập trạng thái ban đầu dựa trên tọa độ
    - Lưu ảnh phụ nếu có
    Trả về: (house, warning_message)
    """
    house = form.save(commit=False)
    house.owner = owner
    manual_lat, manual_lng = _parse_manual_coordinates(request)
    if manual_lat is not None and manual_lng is not None:
        lat, lng, geocode_state = manual_lat, manual_lng, 'manual_pin'
    else:
        lat, lng, geocode_state = _resolve_house_location(house)

    if lat is not None and lng is not None:
        house.lat = lat
        house.lng = lng
        house.requires_coordinates = False
        house.status = 'pending'
    else:
        house.status = 'no_coordinates'
        house.lat = house.lng = None
        house.requires_coordinates = True

    house.save()

    if request is not None:
        save_house_furniture(house, request)

    # Lưu ảnh phụ
    if images:
        for image in images:
            HouseImage.objects.create(house=house, image=image)

    if geocode_state in {'geocoded_nominatim', 'cached', 'parsed_from_input'}:
        warning_msg = 'Hệ thống đã tự động lấy tọa độ từ địa chỉ. Tin đăng đang chờ duyệt.'
    elif geocode_state == 'manual_pin':
        warning_msg = 'Hệ thống đã ghi nhận tọa độ theo vị trí bạn ghim trên bản đồ. Tin đăng đang chờ duyệt.'
    else:
        warning_msg = 'Không thể tự động xác định tọa độ từ địa chỉ. Vui lòng kiểm tra lại địa chỉ để hệ thống thử lại.'
    return house, warning_msg


def update_house(form, owner, original_address, request=None):
    """
    Cập nhật thông tin bài đăng nhà.
    - Xử lý logic trạng thái tọa độ khi địa chỉ thay đổi
    Trả về: (house, warning_message hoặc None)
    """
    house = form.save(commit=False)
    house.owner = owner
    warning_msg = None


    original_address_norm = (original_address or '').strip()
    new_address_norm = (house.address or '').strip()

    location_changed = (
        original_address_norm != new_address_norm
    )

    manual_lat, manual_lng = _parse_manual_coordinates(request)
    
    pin_moved = False
    if manual_lat is not None and manual_lng is not None:
        if house.lat is None or house.lng is None:
            pin_moved = True
        elif abs(house.lat - manual_lat) > 0.0001 or abs(house.lng - manual_lng) > 0.0001:
            pin_moved = True

    need_geocode = location_changed or house.lat is None or house.lng is None or pin_moved
    if need_geocode:
        if pin_moved:
            lat, lng, geocode_state = manual_lat, manual_lng, 'manual_pin'
        else:
            lat, lng, geocode_state = _resolve_house_location(house)

        if lat is not None and lng is not None:
            house.lat = lat
            house.lng = lng
            house.requires_coordinates = False
            house.status = 'pending'
            if geocode_state == 'manual_pin':
                if not location_changed:
                    warning_msg = 'Đã cập nhật tọa độ theo vị trí bạn ghim trên bản đồ. Tin đăng đang chờ duyệt lại.'
                else:
                    warning_msg = 'Đã cập nhật vị trí theo điểm bạn ghim trên bản đồ. Tin đăng đang chờ duyệt lại.'
            elif location_changed:
                warning_msg = 'Đã thay đổi vị trí và hệ thống đã tự động cập nhật tọa độ mới. Tin đăng đang chờ duyệt lại.'
            else:
                warning_msg = 'Hệ thống đã tự động bổ sung tọa độ cho tin đăng.'
        elif manual_lat is not None and manual_lng is not None:
            # Fallback to the pin that was already on the map if geocoding fails
            house.lat = manual_lat
            house.lng = manual_lng
            house.requires_coordinates = False
            house.status = 'pending'
            warning_msg = 'Không tự động tìm được tọa độ từ địa chỉ mới, hệ thống giữ lại vị trí ghim hiện tại trên bản đồ.'
        else:
            house.lat = house.lng = None
            house.requires_coordinates = True
            house.status = 'no_coordinates'
            if location_changed:
                warning_msg = 'Đã thay đổi vị trí nhưng chưa tự động lấy được tọa độ. Vui lòng kiểm tra lại địa chỉ hoặc ghim thủ công trên bản đồ.'
            else:
                warning_msg = 'Tin đăng chưa có tọa độ và hệ thống chưa thể tự động xác định từ địa chỉ hiện tại.'
    else:
        house.requires_coordinates = False

    house.save()

    if request is not None:
        save_house_furniture(house, request)

    return house, warning_msg


def delete_house(house_id, owner):
    """
    Xóa bài đăng nhà (chỉ chủ nhà mới được xóa).
    Trả về: True nếu xóa thành công
    """
    from django.shortcuts import get_object_or_404
    house = get_object_or_404(House, id=house_id, owner=owner)
    house.delete()
    return True


def get_user_houses(owner, query='', status=''):
    """
    Lấy danh sách nhà của chủ nhà, có hỗ trợ tìm kiếm và lọc theo trạng thái.
    Trả về: (queryset, status_choices)
    """
    user_houses = House.objects.filter(owner=owner)

    if query:
        user_houses = user_houses.filter(name__icontains=query)

    valid_status_values = {choice[0] for choice in House.STATUS_CHOICES}
    if status in valid_status_values:
        user_houses = user_houses.filter(status=status)

    status_choices = [(v, l, v == status) for v, l in House.STATUS_CHOICES]

    return user_houses.order_by('-created_at'), status_choices



# ==================== ADMIN SERVICES ====================


def approve_house(house):
    """ Admin duyệt nhà """
    if house.lat is None or house.lng is None:
        house.status = 'no_coordinates'
        house.requires_coordinates = True    
        house.save(update_fields=['status', 'requires_coordinates'])
        return False, f'Không thể duyệt "{house.name}" vì chưa có tọa độ. Vui lòng nhập kinh độ/vĩ độ trước.'
    
    house.status = 'available'
    house.requires_coordinates = False
    house.save(update_fields=['status', 'requires_coordinates'])
    return True, f"Đã duyệt bài đăng: {house.name}"

def reject_house(house):
    """ Admin từ chối nhà """
    house.status = 'rejected'
    house.save(update_fields=['status'])
    return True, f'Đã từ chối bài đăng: {house.name}'

def mark_as_rented(house):
    """ Đánh dấu nhà đã được cho thuê khi có người kí hợp đồng"""
    house.status = 'rented'
    house.save(update_fields=['status'])
    return house


# ==================== PUBLIC QUERY SERVICES ====================

def get_latest_available_houses(limit=6):
    """
    Lấy danh sách nhà mới nhất đang còn trống (cho trang chủ).
    """
    return House.objects.filter(status='available').order_by('-created_at')[:limit]


def get_house_detail(house_id):
    """
    Lấy thông tin chi tiết 1 nhà + danh sách nhà liên quan cùng quận.
    Trả về: (house, related_houses)
    """
    from django.shortcuts import get_object_or_404

    house = get_object_or_404(
        House.objects.prefetch_related('furniture_items__furniture'),
        id=house_id,
    )
    related_houses = House.objects.filter(
        status='available',
    ).exclude(id=house_id)[:3]
    other_houses = House.objects.filter(
        status='available',
        owner=house.owner,
    ).exclude(id=house_id).order_by('-created_at')[:6]
    return house, related_houses, other_houses


def get_map_houses():
    """
    Lấy danh sách nhà có tọa độ hợp lệ để hiển thị trên bản đồ.
    Trả về: list[dict] chứa thông tin cần render trên map
    """
    from django.urls import reverse

    approved_houses = House.objects.filter(
        status__in=['available', 'rented'],
        lat__isnull=False,
        lng__isnull=False,
    ).order_by('-created_at')

    return [{
        'name': house.name,
        'price': f"{house.price:,} VNĐ/tháng" if house.price else 'Thỏa thuận',
        'status': house.get_status_display(),
        'lat': house.lat,
        'lng': house.lng,
        'detail_url': reverse('house_detail', args=[house.id]),
    } for house in approved_houses]

