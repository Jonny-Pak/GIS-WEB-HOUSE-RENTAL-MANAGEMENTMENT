from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from houses.models import House, HouseImage
from houses.forms import HouseForm

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard/overview.html')

@login_required(login_url='login')
def post_house(request):
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            house = form.save(commit=False)
            house.owner = request.user
            house.status = 'no_coordinates'
            house.lat = house.lng = None
            house.requires_coordinates = True
            house.save()
            for image in request.FILES.getlist('detail_images'):
                HouseImage.objects.create(house=house, image=image)
            messages.warning(request, 'Tin đăng đang ở trạng thái Chưa có tọa độ. Admin sẽ nhập tọa độ thủ công trước khi duyệt.')
            messages.success(request, 'Đăng thông tin nhà thành công!')
            return redirect('manage_post')
    else:
        form = HouseForm()
    return render(request, 'dashboard/post_house.html', {'form': form})

@login_required(login_url='login')
def manage_post(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    user_houses = House.objects.filter(owner=request.user)
    if query:
        user_houses = user_houses.filter(name__icontains=query)
    valid_status_values = {choice[0] for choice in House.STATUS_CHOICES}
    if status in valid_status_values:
        user_houses = user_houses.filter(status=status)
    status_choices = [(v, l, v == status) for v, l in House.STATUS_CHOICES]
    return render(request, 'dashboard/manage_post.html', {
        'user_houses': user_houses.order_by('-created_at'),
        'query': query,
        'selected_status': status,
        'status_choices': status_choices,
    })

@login_required(login_url='login')
def edit_house(request, house_id):
    house = get_object_or_404(House, id=house_id, owner=request.user)
    original_address = house.address
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES, instance=house)
        if form.is_valid():
            updated_house = form.save(commit=False)
            updated_house.owner = request.user
            if (original_address or '').strip() != (updated_house.address or '').strip():
                updated_house.lat = updated_house.lng = None
                updated_house.requires_coordinates = True
                updated_house.status = 'no_coordinates'
                messages.warning(request, 'Bạn đã thay đổi địa chỉ. Tin đăng chuyển về trạng thái Chưa có tọa độ.')
            elif updated_house.lat is None or updated_house.lng is None:
                updated_house.requires_coordinates = True
                updated_house.status = 'no_coordinates'
            else:
                updated_house.requires_coordinates = False
            updated_house.save()
            messages.success(request, 'Cập nhật thông tin nhà thành công!')
            return redirect('manage_post')
    else:
        form = HouseForm(instance=house)
    return render(request, 'dashboard/post_house.html', {'form': form})

@require_POST
@login_required(login_url='login')
def delete_house(request, house_id):
    get_object_or_404(House, id=house_id, owner=request.user).delete()
    messages.success(request, 'Đã xóa bài đăng thành công!')
    return redirect('manage_post')
