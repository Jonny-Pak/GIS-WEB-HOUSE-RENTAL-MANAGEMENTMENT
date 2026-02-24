import math
from shapely.geometry import Point, Polygon
from .models import House

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
