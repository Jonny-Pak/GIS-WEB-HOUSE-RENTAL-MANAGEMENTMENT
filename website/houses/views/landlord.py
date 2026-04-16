from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from houses.models import House
from houses.forms import HouseForm
from houses.services.geocoding import resolve_house_coordinates
from houses.services.house_service import (
    build_furniture_choices,
    create_house,
    delete_house,
    get_user_houses,
    update_house,
)

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard/overview.html')

@login_required(login_url='login')
def post_house(request):
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            house, warning_msg = create_house(
                form=form,
                owner=request.user,
                images=request.FILES.getlist('detail_images'),
                request=request,
            )
            if warning_msg:
                messages.warning(request, warning_msg)
            messages.success(request, 'Đăng thông tin nhà thành công!')
            return redirect('manage_post')
    else:
        form = HouseForm()
    return render(request, 'dashboard/post_house.html', {
        'form': form,
        'furniture_choices': build_furniture_choices(
            request=request if request.method == 'POST' else None,
        ),
    })

@login_required(login_url='login')
def manage_post(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    user_houses, status_choices = get_user_houses(
        owner=request.user,
        query=query,
        status=status,
    )

    return render(request, 'dashboard/manage_post.html', {
        'user_houses': user_houses,
        'query': query,
        'selected_status': status,
        'status_choices': status_choices,
    })

@login_required(login_url='login')
def edit_house(request, house_id):
    house = get_object_or_404(House.objects.prefetch_related('furniture_items'), id=house_id, owner=request.user)
    original_address = house.address
    original_district = house.district
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES, instance=house)
        if form.is_valid():
            updated_house, warning_msg = update_house(
                form=form,
                owner=request.user,
                original_address=original_address,
                original_district=original_district,
                request=request,
            )
            if warning_msg:
                messages.warning(request, warning_msg)
            messages.success(request, 'Cập nhật thông tin nhà thành công!')
            return redirect('manage_post')
    else:
        form = HouseForm(instance=house)
    return render(request, 'dashboard/post_house.html', {
        'form': form,
        'furniture_choices': build_furniture_choices(
            request=request if request.method == 'POST' else None,
            house=house,
        ),
    })

@require_POST
@login_required(login_url='login')
def delete_house_view(request, house_id):
    delete_house(house_id=house_id, owner=request.user)
    messages.success(request, 'Đã xóa bài đăng thành công!')
    return redirect('manage_post')


@require_POST
@login_required(login_url='login')
def geocode_preview(request):
    address = (request.POST.get('address') or '').strip()

    if not address:
        return JsonResponse({
            'success': False,
            'message': 'Vui lòng nhập địa chỉ để lấy tọa độ.',
        })

    user_lat_str = request.POST.get('user_lat')
    user_lng_str = request.POST.get('user_lng')
    user_lat = None
    user_lng = None
    try:
        if user_lat_str and user_lng_str:
            user_lat = float(user_lat_str)
            user_lng = float(user_lng_str)
    except ValueError:
        pass

    from houses.services.geocoding import resolve_house_coordinates
    lat, lng, state = resolve_house_coordinates(
        address=address,
        user_lat=user_lat,
        user_lng=user_lng
    )

    approximate_states = {'district_center_fallback', 'district_center_fallback_rate_limited'}

    if lat is None or lng is None or state in approximate_states:
        if state == 'nominatim_rate_limited':
            message = 'Dịch vụ bản đồ OpenStreetMap đang quá tải (429). Hãy thử lại sau ít phút.'
        elif state in approximate_states:
            message = 'Không tìm được tọa độ chính xác theo địa chỉ. Hãy click lên bản đồ để ghim vị trí thủ công.'
        else:
            message = 'Chưa tìm thấy tọa độ phù hợp từ địa chỉ này. Hãy thêm chi tiết số nhà, đường và phường/xã.'

        return JsonResponse({
            'success': False,
            'message': message,
            'source': state,
            'approximate_lat': float(lat) if lat is not None else None,
            'approximate_lng': float(lng) if lng is not None else None,
        })

    if state == 'district_center_fallback':
        message = 'OpenStreetMap chưa định vị chính xác được chuỗi địa chỉ này. Hệ thống tạm lấy tọa độ trung tâm quận/huyện đã chọn.'
    elif state == 'district_center_fallback_rate_limited':
        message = 'OpenStreetMap đang quá tải tạm thời. Hệ thống đã dùng tọa độ trung tâm quận/huyện để bạn không bị gián đoạn.'
    elif state == 'parsed_from_input':
        message = 'Đã đọc trực tiếp tọa độ từ nội dung bạn nhập.'
    elif state == 'cached':
        message = 'Đã dùng tọa độ đã lưu trước đó cho địa chỉ này.'
    else:
        message = 'Đã lấy tọa độ thành công.'

    return JsonResponse({
        'success': True,
        'lat': float(lat),
        'lng': float(lng),
        'source': state,
        'message': message,
    })

@require_POST
@login_required(login_url='login')
def reverse_geocode_preview(request):
    try:
        lat = float(request.POST.get('lat', ''))
        lng = float(request.POST.get('lng', ''))
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Tọa độ không hợp lệ.'})

    from houses.services.geocoding import reverse_geocode_nominatim
    address = reverse_geocode_nominatim(lat, lng)

    if address:
        return JsonResponse({'success': True, 'address': address})
    else:
        return JsonResponse({'success': False, 'message': 'Không thể lấy địa chỉ từ tọa độ này.'})
