import logging

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect
from django.shortcuts import render

from houses.forms import SupportRequestForm
from houses.models import House
from houses.services.house_service import (
    get_house_detail,
    get_map_houses,
)


logger = logging.getLogger(__name__)


def home(request):
    houses_qs = House.objects.filter(status='available').order_by('-created_at')

    # Trạng thái lọc
    search_query = request.GET.get('search', '').strip()
    price_range = request.GET.get('price_range', '').strip()
    area_range = request.GET.get('area_range', '').strip()
    house_type = request.GET.get('house_type', '').strip()

    # Cấu hình Mức giá
    price_range_items = [
        {'value': '0-1', 'label': 'Dưới 1 triệu', 'min': 0, 'max': 1000000},
        {'value': '1-3', 'label': '1 - 3 triệu', 'min': 1000000, 'max': 3000000},
        {'value': '3-5', 'label': '3 - 5 triệu', 'min': 3000000, 'max': 5000000},
        {'value': '5-10', 'label': '5 - 10 triệu', 'min': 5000000, 'max': 10000000},
        {'value': '10-40', 'label': '10 - 40 triệu', 'min': 10000000, 'max': 40000000},
        {'value': '40-70', 'label': '40 - 70 triệu', 'min': 40000000, 'max': 70000000},
        {'value': '70-100', 'label': '70 - 100 triệu', 'min': 70000000, 'max': 100000000},
        {'value': '100-max', 'label': 'Trên 100 triệu', 'min': 100000000, 'max': 999999999},
    ]

    # Cấu hình Diện tích
    area_range_items = [
        {'value': '0-30', 'label': 'Dưới 30 m²', 'min': 0, 'max': 30},
        {'value': '30-50', 'label': '30 - 50 m²', 'min': 30, 'max': 50},
        {'value': '50-80', 'label': '50 - 80 m²', 'min': 50, 'max': 80},
        {'value': '80-100', 'label': '80 - 100 m²', 'min': 80, 'max': 100},
        {'value': '100-150', 'label': '100 - 150 m²', 'min': 100, 'max': 150},
        {'value': '150-200', 'label': '150 - 200 m²', 'min': 150, 'max': 200},
        {'value': '200-250', 'label': '200 - 250 m²', 'min': 200, 'max': 250},
        {'value': '250-300', 'label': '250 - 300 m²', 'min': 250, 'max': 300},
        {'value': '300-max', 'label': 'Trên 300 m²', 'min': 300, 'max': 9999},
    ]

    # Áp dụng bộ lọc Nhà
    if search_query:
        houses_qs = houses_qs.filter(
            Q(name__icontains=search_query) | 
            Q(address__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # Lọc Giá
    selected_price = next((item for item in price_range_items if item['value'] == price_range), None)
    if selected_price:
        houses_qs = houses_qs.filter(price__gte=selected_price['min'], price__lte=selected_price['max'])

    # Lọc Diện tích
    selected_area = next((item for item in area_range_items if item['value'] == area_range), None)
    if selected_area:
        houses_qs = houses_qs.filter(area__gte=selected_area['min'], area__lte=selected_area['max'])

    # Lọc Loại nhà
    house_type_items = [{'value': v, 'label': l, 'selected': house_type == v} for v, l in House.HOUSE_TYPE_CHOICES]
    if house_type:
        houses_qs = houses_qs.filter(house_type=house_type)

    total_available_rooms = houses_qs.count()

    # Phân trang
    try:
        page = max(int(request.GET.get('page', '1')), 1)
    except ValueError:
        page = 1
    
    per_page = 12
    paginator = Paginator(houses_qs, per_page)
    try:
        houses_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        houses_page = paginator.page(1)

    context = {
        'page_obj': houses_page,
        'houses': houses_page.object_list,
        'total_available_rooms': total_available_rooms,
        'price_range_items': price_range_items,
        'area_range_items': area_range_items,
        'house_type_items': house_type_items,
        'filters': {
            'search': search_query,
            'price_range': price_range,
            'area_range': area_range,
            'house_type': house_type,
        },
    }
    return render(request, 'home.html', context)
    return render(request, 'home.html', context)


def house_detail_view(request, house_id):
    house, related_houses, other_houses = get_house_detail(house_id)
    return render(request, 'houses/house_detail.html', {
        'house': house,
        'related_houses': related_houses,
        'other_houses': other_houses,
    })


def map_view(request):
    map_houses = get_map_houses()
    return render(request, 'houses/map_static.html', {'map_houses': map_houses})


def support_view(request):
    initial = {}
    if request.user.is_authenticated:
        initial['full_name'] = request.user.get_full_name() or request.user.username
        initial['contact_email'] = request.user.email

    if request.method == 'POST':
        form = SupportRequestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            subject = f"[SUPPORT] {data['subject']}"
            body = (
                'Yeu cau ho tro moi\n'
                f"Ho ten: {data['full_name']}\n"
                f"Email lien he: {data['contact_email']}\n"
                f"Tai khoan gui: {request.user.username if request.user.is_authenticated else 'Khach'}\n\n"
                f"Noi dung:\n{data['message']}"
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [settings.SUPPORT_INBOX_EMAIL]

            try:
                email = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=from_email,
                    to=to_email,
                    reply_to=[data['contact_email']],
                )
                email.send(fail_silently=False)
                messages.success(request, 'Yeu cau ho tro da duoc gui. Chung toi se lien he som nhat!')
                return redirect('support')
            except Exception:
                logger.exception('Support request email failed to send')
                messages.error(
                    request,
                    'Khong the gui yeu cau ho tro luc nay. Vui long thu lai sau hoac lien he hotline ben duoi.',
                )
    else:
        form = SupportRequestForm(initial=initial)

    return render(
        request,
        'support.html',
        {
            'support_form': form,
            'support_hotline': settings.SUPPORT_CONTACT_PHONE,
            'support_email': settings.SUPPORT_INBOX_EMAIL,
        },
    )


def error_403(request, exception):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)
