from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from quanly.service import get_nearby_houses_qs, get_houses_in_polygon_qs
from quanly.serializers import HouseSerializer

@api_view(['GET'])
def api_houses(request):
    """API tìm kiếm theo bán kính (Áp dụng DRF)"""
    try:
        lat_str = request.GET.get('lat')
        lng_str = request.GET.get('lng')
        
        if lat_str is None or lng_str is None:
            return Response({"error": "Vui lòng cung cấp tham số 'lat' và 'lng'"}, status=status.HTTP_400_BAD_REQUEST)
            
        lat = float(lat_str)
        lng = float(lng_str)
        radius = float(request.GET.get('radius', 5))
        
        # Gọi Service để lấy dữ liệu QuerySet/List thô
        houses_qs = get_nearby_houses_qs(lat, lng, radius)
        
        # Dùng Serializer để tự động format JSON
        serializer = HouseSerializer(houses_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValueError:
        return Response({"error": "Cấu trúc tham số không hợp lệ (lat, lng, radius phải là số)"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def api_polygon_search(request):
    """API tìm kiếm theo vùng vẽ (Áp dụng DRF)"""
    coords = request.data.get('coords', [])
    
    if not isinstance(coords, list) or len(coords) == 0:
        return Response({"error": "Thiếu tọa độ vùng vẽ hoặc định dạng không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        houses_qs = get_houses_in_polygon_qs(coords)
        serializer = HouseSerializer(houses_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Lỗi máy chủ: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
