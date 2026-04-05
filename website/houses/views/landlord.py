from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from houses.models import House
from houses.forms import HouseForm
from houses.services.house_service import (
    create_house, update_house, delete_house, get_user_houses,
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
            )
            messages.warning(request, warning_msg)
            messages.success(request, 'Đăng thông tin nhà thành công!')
            return redirect('manage_post')
    else:
        form = HouseForm()
    return render(request, 'dashboard/post_house.html', {'form': form})

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
    house = get_object_or_404(House, id=house_id, owner=request.user)
    original_address = house.address
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES, instance=house)
        if form.is_valid():
            updated_house, warning_msg = update_house(
                form=form,
                owner=request.user,
                original_address=original_address,
            )
            if warning_msg:
                messages.warning(request, warning_msg)
            messages.success(request, 'Cập nhật thông tin nhà thành công!')
            return redirect('manage_post')
    else:
        form = HouseForm(instance=house)
    return render(request, 'dashboard/post_house.html', {'form': form})

@require_POST
@login_required(login_url='login')
def delete_house_view(request, house_id):
    delete_house(house_id=house_id, owner=request.user)
    messages.success(request, 'Đã xóa bài đăng thành công!')
    return redirect('manage_post')
