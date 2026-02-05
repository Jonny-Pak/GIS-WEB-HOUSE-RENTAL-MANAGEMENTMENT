from django.shortcuts import render
from .service import get_nearby_houses_json, get_houses_in_polygon
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def api_houses(request):
    """API tìm kiếm theo bán kính (GET)"""
    try:
        lat = float(request.GET.get('lat', 0))
        lng = float(request.GET.get('lng', 0))
        radius = float(request.GET.get('radius', 5))
        
        data = get_nearby_houses_json(lat, lng, radius)
        return JsonResponse(data, safe=False)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Tham số không hợp lệ"}, status=400)

# Create your views here.
@csrf_exempt
def api_polygon_search(request):
    """API tìm kiếm theo vùng vẽ (POST)"""
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            coords = body.get('coords', [])
            if not coords:
                return JsonResponse({"error": "Thiếu tọa độ vùng vẽ"}, status=400)
            
            data = get_houses_in_polygon(coords)
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
    
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
