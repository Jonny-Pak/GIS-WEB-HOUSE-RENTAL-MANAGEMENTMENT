from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from quanly.models import House

def home(request):
    return render(request, 'quanly/home.html')

def register(request):
    return render(request, 'quanly/accounts/register.html')

def home_details_view(request):
    return render(request, 'quanly/houses/house_detail.html')


def map_view(request):
    approved_houses = House.objects.filter(
        status='available',
        lat__isnull=False,
        lng__isnull=False,
    ).order_by('-created_at')

    map_houses = []
    for house in approved_houses:
        map_houses.append({
            'name': house.name,
            'price': f"{house.price:,} VNĐ/thang" if house.price else 'Thoa thuan',
            'district': house.get_district_display(),
            'lat': house.lat,
            'lng': house.lng,
            'detail_url': reverse('home_details'),
        })

    return render(request, 'quanly/houses/map_static.html', {
        'map_houses': map_houses,
    })

@login_required 
def profile_view(request):
    return render(request, 'quanly/profile.html', {'user': request.user})
