import math
from shapely.geometry import Point, Polygon
from houses.models import House, HouseImage


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


# ==================== LANDLORD SERVICES ====================

def create_house(form, owner, images=None):
    """
    Tạo mới một bài đăng nhà.
    - Gán chủ nhà (owner)
    - Thiết lập trạng thái ban đầu dựa trên tọa độ
    - Lưu ảnh phụ nếu có
    Trả về: (house, warning_message)
    """
    house = form.save(commit=False)
    house.owner = owner
    house.status = 'no_coordinates'
    house.lat = house.lng = None
    house.requires_coordinates = True
    house.save()

    # Lưu ảnh phụ
    if images:
        for image in images:
            HouseImage.objects.create(house=house, image=image)

    warning_msg = 'Tin đăng đang ở trạng thái Chưa có tọa độ. Admin sẽ nhập tọa độ thủ công trước khi duyệt.'
    return house, warning_msg


def update_house(form, owner, original_address):
    """
    Cập nhật thông tin bài đăng nhà.
    - Xử lý logic trạng thái tọa độ khi địa chỉ thay đổi
    Trả về: (house, warning_message hoặc None)
    """
    house = form.save(commit=False)
    house.owner = owner
    warning_msg = None

    # Nếu địa chỉ thay đổi -> reset tọa độ, chuyển về trạng thái chờ
    if (original_address or '').strip() != (house.address or '').strip():
        house.lat = house.lng = None
        house.requires_coordinates = True
        house.status = 'no_coordinates'
        warning_msg = 'Bạn đã thay đổi địa chỉ. Tin đăng chuyển về trạng thái Chưa có tọa độ.'
    elif house.lat is None or house.lng is None:
        house.requires_coordinates = True
        house.status = 'no_coordinates'
    else:
        house.requires_coordinates = False

    house.save()
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
    house = get_object_or_404(House, id=house_id)
    related_houses = House.objects.filter(district=house.district).exclude(id=house_id)[:3]
    return house, related_houses


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
        'district': house.get_district_display(),
        'status': house.get_status_display(),
        'lat': house.lat,
        'lng': house.lng,
        'detail_url': reverse('house_detail', args=[house.id]),
    } for house in approved_houses]

