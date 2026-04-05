from django.shortcuts import render
from houses.services.house_service import (
    get_latest_available_houses, get_house_detail, get_map_houses,
)

def home(request):
    houses = get_latest_available_houses(limit=6)
    return render(request, 'home.html', {'houses': houses})

def house_detail_view(request, house_id):
    house, related_houses = get_house_detail(house_id)
    return render(request, 'houses/house_detail.html', {'house': house, 'related_houses': related_houses})

def map_view(request):
    map_houses = get_map_houses()
    return render(request, 'houses/map_static.html', {'map_houses': map_houses})
