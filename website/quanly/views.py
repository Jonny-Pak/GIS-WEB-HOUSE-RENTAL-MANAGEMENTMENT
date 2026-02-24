from django.shortcuts import render
from .service import get_nearby_houses_json, get_houses_in_polygon
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def api_houses(request):
    """API tìm kiếm theo bán kính (GET)"""
    if request.method != "GET":
        return JsonResponse({"error": "Phương thức không được phép"}, status=405)
        
    try:
        lat_str = request.GET.get('lat')
        lng_str = request.GET.get('lng')
        
        if lat_str is None or lng_str is None:
            return JsonResponse({"error": "Vui lòng cung cấp tham số 'lat' và 'lng'"}, status=400)
            
        lat = float(lat_str)
        lng = float(lng_str)
        radius = float(request.GET.get('radius', 5))
        
        data = get_nearby_houses_json(lat, lng, radius)
        return JsonResponse(data, safe=False)
    except ValueError:
        return JsonResponse({"error": "Cấu trúc tham số không hợp lệ (lat, lng, radius phải là số)"}, status=400)

# Create your views here.
@csrf_exempt
def api_polygon_search(request):
    """API tìm kiếm theo vùng vẽ (POST)"""
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            coords = body.get('coords', [])
            
            if not isinstance(coords, list) or len(coords) == 0:
                return JsonResponse({"error": "Thiếu tọa độ vùng vẽ hoặc định dạng không hợp lệ"}, status=400)
            
            data = get_houses_in_polygon(coords)
            return JsonResponse(data, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Dữ liệu gửi lên không phải là JSON hợp lệ"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Lỗi máy chủ: {str(e)}"}, status=500)
    return JsonResponse({"error": "Phương thức không được phép"}, status=405)
    
def home(request):
    return render(request, 'quanly/home.html')

def register(request):
    return render(request, 'quanly/accounts/register.html')

def house_detail(request):
    return render(request, 'quanly/houses/house_detail.html')

def dashboard(request):
    return render(request, 'quanly/dashboard/overview.html')

def post_house(request):
    return render(request, 'quanly/dashboard/post_house.html')

def manage_post(request):
    return render(request, 'quanly/dashboard/manage_post.html')
