from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from quanly.models import House

def home(request):
    # Lấy 6 ngôi nhà mới nhất đang ở trạng thái 'đã duyệt'
    houses = House.objects.filter(status='available').order_by('-created_at')[:6]
    context = {
        'houses': houses,
    }
    return render(request, 'quanly/home.html', context)

def register(request):
    return render(request, 'quanly/accounts/register.html')

def house_detail_view(request, house_id):
    house = get_object_or_404(House, id=house_id)
    related_houses = House.objects.filter(district=house.district).exclude(id=house_id)[:3]
    context = {
        'house': house,
        'related_houses': related_houses,
    }
    return render(request, 'quanly/houses/house_detail.html', context)


def map_view(request):
    approved_houses = House.objects.filter(
        status__in=['available', 'rented'],
        lat__isnull=False,
        lng__isnull=False,
    ).order_by('-created_at')

    map_houses = []
    for house in approved_houses:
        map_houses.append({
            'name': house.name,
            'price': f"{house.price:,} VNĐ/tháng" if house.price else 'Thỏa thuận',
            'district': house.get_district_display(),
            'status': house.get_status_display(),
            'lat': house.lat,
            'lng': house.lng,
            'detail_url': reverse('house_detail', args=[house.id]),
        })

    return render(request, 'quanly/houses/map_static.html', {
        'map_houses': map_houses,
    })

@login_required 
def profile_view(request):
    return render(request, 'quanly/profile.html', {'user': request.user})
