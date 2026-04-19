import logging

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from django.core.mail import EmailMessage
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

    search_query = request.GET.get('search', '').strip()
    # district đã loại bỏ
    price_range = request.GET.get('price_range', '').strip()
    house_type = request.GET.get('house_type', '').strip()

    price_range_items = [
        {
            'value': '3-5',
            'label': '3 triệu đến 5 triệu',
            'min_price': 3000000,
            'max_price': 5000000,
        },
        {
            'value': '5-8',
            'label': '5 triệu đến 8 triệu',
            'min_price': 5000000,
            'max_price': 8000000,
        },
        {
            'value': '8-14',
            'label': '8 triệu đến 14 triệu',
            'min_price': 8000000,
            'max_price': 14000000,
        },
        {
            'value': '14-25',
            'label': '14 triệu đến 25 triệu',
            'min_price': 14000000,
            'max_price': 25000000,
        },
    ]

    try:
        page = max(int(request.GET.get('page', '1')), 1)
    except ValueError:
        page = 1

    per_page = 6

    if search_query:
        houses_qs = houses_qs.filter(
            Q(name__icontains=search_query)
            | Q(address__icontains=search_query)
            | Q(description__icontains=search_query)
        )



    selected_price_range = next(
        (item for item in price_range_items if item['value'] == price_range),
        None,
    )
    if selected_price_range:
        houses_qs = houses_qs.filter(
            price__gte=selected_price_range['min_price'],
            price__lte=selected_price_range['max_price'],
        )

    house_type_items = [
        {
            'value': value,
            'label': label,
        }
        for value, label in House.HOUSE_TYPE_CHOICES
    ]

    valid_house_types = {item['value'] for item in house_type_items}
    if house_type in valid_house_types:
        houses_qs = houses_qs.filter(house_type=house_type)

    total_available_rooms = houses_qs.count()

    offset = (page - 1) * per_page
    houses = list(houses_qs[offset:offset + per_page + 1])
    has_more_houses = len(houses) > per_page
    if has_more_houses:
        houses = houses[:per_page]


    context = {
        'houses': houses,
        'has_more_houses': has_more_houses,
        'next_page': page + 1,
        'total_available_rooms': total_available_rooms,
        'price_range_items': price_range_items,
        'house_type_items': house_type_items,
        'filters': {
            'search': search_query,
            'price_range': price_range,
            'house_type': house_type,
        },
    }
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
