from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from .models import House

def get_nearby_houses_json(user_lat, user_long, radius_km=5):
    # Lọc những nhà ở trạng thái 'available' (Đang cho thuê)
    # Sử dụng Point(longitude, latitude) - Chú ý thứ tự chuẩn GIS
    user_location = Point(user_long, user_lat, srid=4326)
    
    # Tìm kiếm không gian bằng PostGIS (distance_lte = DWithin)
    houses = House.objects.filter(
        status='available',
        location__distance_lte=(user_location, D(km=radius_km))
    ).annotate(
        distance_to_user=Distance('location', user_location)
    )
    
    nearby_houses = []
    for house in houses:
        # Lấy khoảng cách chính xác từ DB đã annotate (trả về km)
        distance = house.distance_to_user.km if getattr(house, 'distance_to_user', None) else 0
        
        nearby_houses.append({
            "id": house.id,
            "name": house.name,
            "price": house.price,
            "district": house.get_district_display(),
            "image": house.main_image.url if house.main_image else None,
            "distance": round(distance, 2),
            "coords": {"lat": house.location.y, "lng": house.location.x}
        })
    return nearby_houses


def get_houses_in_polygon(polygon_coords):
    """
    Input: List các tuple tọa độ [(lng1, lat1), (lng2, lat2), ...] hoặc format tương tự
    Output: Danh sách các dict nhà nằm trong vùng
    """
    if len(polygon_coords) >= 3:
        # Chuyển đổi thành dạng tuple x, y (lng, lat)
        formatted_coords = [(float(pt.get('lng', 0)), float(pt.get('lat', 0))) for pt in polygon_coords]

        # Nếu polygon không khép kín (điểm đầu != điểm cuối), tự động khép kín
        if formatted_coords[0] != formatted_coords[-1]:
            formatted_coords.append(formatted_coords[0])
            
        # Một polygon hợp lệ trong GEOS yêu cầu tối thiểu 4 điểm (bao gồm cả điểm khép kín)
        if len(formatted_coords) < 4:
            return []
            
        # Tạo GEOSGeometry Polygon (Lưu ý: Input của Polygon trong GEOS là tuple của các tuple)
        poly = Polygon(tuple(formatted_coords), srid=4326)
        
        # Truy vấn nhà nằm trong (within) Đa giác
        houses = House.objects.filter(
            status='available',
            location__within=poly
        )
    else:
        # Trả về rỗng nếu không đủ điểm tạo đa giác
        return []

    results = []
    for house in houses:
        image_url = house.main_image.url if house.main_image else "/static/images/default.jpg"
        results.append({
            "id": house.id,
            "name": house.name,
            "price": house.price,
            "address": house.address,
            "district": house.get_district_display(),
            "image": image_url,
            "coords": {"lat": house.location.y, "lng": house.location.x}
        })
        
    return results
