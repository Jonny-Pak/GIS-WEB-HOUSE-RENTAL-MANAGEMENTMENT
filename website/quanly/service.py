import math
from .models import House
from shapely.geometry import Point, Polygon as ShapePolygon

def get_nearby_houses_json(user_lat, user_long, radius_km=5):
    # Lọc những nhà ở trạng thái 'approved' (Đã duyệt)
    houses = House.objects.filter(status='approved') 
    nearby_houses = []

    for house in houses:
        # Thuật toán Haversine tính khoảng cách
        R = 6371 
        dlat = math.radians(house.lat - user_lat)
        dlong = math.radians(house.long - user_long)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(user_lat)) * math.cos(math.radians(house.lat)) *
             math.sin(dlong / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        if distance <= radius_km:
            nearby_houses.append({
                "id": house.id,
                "name": house.name,
                "price": house.price,
                "district": house.get_district_display(), # Lấy tên Quận hiển thị
                "image": house.main_image.url if house.main_image else None,
                "distance": round(distance, 2),
                "coords": {"lat": house.lat, "lng": house.long}
            })
    return nearby_houses

    # Gợi ý thêm logic tính khoảng cách đơn giản trong models.py hoặc views.py
# from geopy.distance import geodesic

# def get_houses_nearby(user_lat, user_long, radius_km=5):
#     houses = House.objects.all()
#     nearby_houses = []
#     for house in houses:
#         distance = geodesic((user_lat, user_long), (house.lat, house.long)).km
#         if distance <= radius_km:
#             nearby_houses.append(house)
#     return nearby_houses

def get_houses_in_polygon(polygon_coords):
    """
    Input: List các tuple tọa độ [(lat1, lng1), (lat2, lng2), ...]
    Output: Danh sách các dict nhà nằm trong vùng
    """
    # 1. Tạo đối tượng Đa giác từ tọa độ người dùng vẽ
    poly = ShapePolygon(polygon_coords)
    
    # 2. Lấy danh sách nhà đã duyệt
    houses = House.objects.filter(status='approved')
    results = []

    for house in houses:
        # 3. Tạo điểm từ tọa độ của căn nhà
        pnt = Point(house.lat, house.long)
        
        # 4. Kiểm tra điểm có nằm TRONG đa giác không
        if poly.contains(pnt):
            image_url = house.main_image.url if house.main_image else "/static/images/default.jpg"
            results.append({
                "id": house.id,
                "name": house.name,
                "price": house.price,
                "address": house.address,
                "district": house.get_district_display(),
                "image": image_url,
                "coords": {"lat": house.lat, "lng": house.long}
            })
            
    return results