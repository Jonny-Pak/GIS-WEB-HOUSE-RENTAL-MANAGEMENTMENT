from django.shortcuts import render
from .service import get_nearby_houses_json
from django.http import JsonResponse

def api_houses(request):
    lat = float(request.GET.get('lat', 21.0285))
    lon = float(request.GET.get('lon', 105.8542) or request.GET.get('lng') or 105.8542)
    radius = float(request.GET.get('radius', 5))

    data = get_nearby_houses_json(lat, lon, radius)

    return JsonResponse(data, safe=False)

# Create your views here.
