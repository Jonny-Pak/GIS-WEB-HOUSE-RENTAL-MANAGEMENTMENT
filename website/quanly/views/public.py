from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.files.storage import default_storage
from quanly.models import House

def home(request):
    search_query = request.GET.get('search', '').strip()
    selected_district = request.GET.get('quan', '').strip()
    selected_price = request.GET.get('gia', '').strip()
    selected_house_type = request.GET.get('loai', '').strip()

    houses_qs = House.objects.filter(status='available').order_by('-created_at')

    if search_query:
        houses_qs = houses_qs.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query)
        )

    district_values = {value for value, _ in House.DISTRICT_CHOICES}
    if selected_district in district_values:
        houses_qs = houses_qs.filter(district=selected_district)
    else:
        selected_district = ''

    if selected_price == '0-5':
        houses_qs = houses_qs.filter(price__isnull=False, price__lt=5_000_000)
    elif selected_price == '5-10':
        houses_qs = houses_qs.filter(price__gte=5_000_000, price__lte=10_000_000)
    elif selected_price == '10-plus':
        houses_qs = houses_qs.filter(price__gt=10_000_000)
    else:
        selected_price = ''

    house_type_values = {value for value, _ in House.HOUSE_TYPE_CHOICES}
    if selected_house_type in house_type_values:
        houses_qs = houses_qs.filter(house_type=selected_house_type)
    else:
        selected_house_type = ''

    paginator = Paginator(houses_qs, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    pagination_query_params = request.GET.copy()
    pagination_query_params.pop('page', None)

    context = {
        'houses': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_district': selected_district,
        'selected_price': selected_price,
        'selected_house_type': selected_house_type,
        'district_choices': House.DISTRICT_CHOICES,
        'house_type_choices': House.HOUSE_TYPE_CHOICES,
        'pagination_query': pagination_query_params.urlencode(),
    }
    return render(request, 'quanly/home.html', context)

def register(request):
    return render(request, 'quanly/accounts/register.html')

def house_detail_view(request, house_id):
    house = get_object_or_404(House, id=house_id)
    related_houses = House.objects.filter(district=house.district).exclude(id=house_id)[:3]

    # Hide broken gallery entries when image files are missing on disk.
    gallery_images = [
        img for img in house.images.all()
        if img.image and default_storage.exists(img.image.name)
    ]

    context = {
        'house': house,
        'related_houses': related_houses,
        'gallery_images': gallery_images,
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
