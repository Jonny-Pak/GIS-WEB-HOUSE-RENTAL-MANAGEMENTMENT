from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from houses.models import House

def home(request):
    houses = House.objects.filter(status='available').order_by('-created_at')[:6]
    return render(request, 'home.html', {'houses': houses})

def house_detail_view(request, house_id):
    house = get_object_or_404(House, id=house_id)
    related_houses = House.objects.filter(district=house.district).exclude(id=house_id)[:3]
    return render(request, 'houses/house_detail.html', {'house': house, 'related_houses': related_houses})

def map_view(request):
    approved_houses = House.objects.filter(
        status__in=['available', 'rented'],
        lat__isnull=False,
        lng__isnull=False,
    ).order_by('-created_at')
    map_houses = [{
        'name': house.name,
        'price': f"{house.price:,} VNĐ/tháng" if house.price else 'Thỏa thuận',
        'district': house.get_district_display(),
        'status': house.get_status_display(),
        'lat': house.lat,
        'lng': house.lng,
        'detail_url': reverse('house_detail', args=[house.id]),
    } for house in approved_houses]
    return render(request, 'houses/map_static.html', {'map_houses': map_houses})
