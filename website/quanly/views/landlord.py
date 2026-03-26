from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from quanly.models import House, HouseImage, Tenant, Contract
from quanly.forms import HouseForm, TenantForm, ContractForm

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'quanly/dashboard/overview.html')

@login_required(login_url='login')
def post_house(request):
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            house = form.save(commit=False)
            house.owner = request.user
            house.status = 'no_coordinates'
            house.lat = None
            house.lng = None
            house.requires_coordinates = True

            house.save()
            
            # Save detail gallery images
            detail_images = request.FILES.getlist('detail_images')
            for image in detail_images:
                HouseImage.objects.create(house=house, image=image)

            messages.warning(
                request,
                'Tin đăng đang ở trạng thái Chưa có tọa độ. Admin sẽ nhập tọa độ thủ công trước khi duyệt.'
            )
            messages.success(request, 'Đăng thông tin nhà thành công!')
            return redirect('manage_post')
    else:
        form = HouseForm()
    return render(request, 'quanly/dashboard/post_house.html', {'form': form})

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
    else:
        status = ''

    status_choices = [
        (value, label, value == status)
        for value, label in House.STATUS_CHOICES
    ]

    user_houses = user_houses.order_by('-created_at')

    return render(request, 'quanly/dashboard/manage_post.html', {
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
            updated_house = form.save(commit=False)
            updated_house.owner = request.user
            address_changed = (original_address or '').strip() != (updated_house.address or '').strip()
            if address_changed:
                updated_house.lat = None
                updated_house.lng = None
                updated_house.requires_coordinates = True
                updated_house.status = 'no_coordinates'
                messages.warning(
                    request,
                    'Bạn đã thay đổi địa chỉ. Tin đăng chuyển về trạng thái Chưa có tọa độ để admin nhập tay trước khi duyệt lại.'
                )
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

    return render(request, 'quanly/dashboard/post_house.html', {'form': form})

@require_POST
@login_required(login_url='login')
def delete_house(request, house_id):
    house = get_object_or_404(House, id=house_id, owner=request.user)
    house.delete()
    messages.success(request, 'Đã xóa bài đăng thành công!')
    return redirect('manage_post')

@login_required(login_url='login')
def create_contract(request, house_id):
    # Ensure house exists and belongs to the logged-in user
    house = get_object_or_404(House, id=house_id, owner=request.user)
    
    # Do not allow creating contract if it's already rented
    if house.status == 'rented':
        messages.error(request, 'Căn nhà này đã được cho thuê, không thể tạo thêm hợp đồng.')
        return redirect('manage_post')

    if request.method == 'POST':
        tenant_form = TenantForm(request.POST, request.FILES)
        contract_form = ContractForm(request.POST, request.FILES)

        if tenant_form.is_valid() and contract_form.is_valid():
            # Create Tenant first
            tenant = tenant_form.save(commit=False)
            tenant.created_by = request.user
            tenant.save()

            # Create Contract linked to Tenant and House
            contract = contract_form.save(commit=False)
            contract.house = house
            contract.renter = tenant
            contract.status = 'active'
            contract.save()

            # Update House Status to Rented
            house.status = 'rented'
            house.save()

            messages.success(request, f'Đã tạo hợp đồng thành công cho căn nhà: {house.name}!')
            return redirect('manage_post')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin biểu mẫu.')
    else:
        tenant_form = TenantForm()
        contract_form = ContractForm()

    return render(request, 'quanly/dashboard/create_contract.html', {
        'house': house,
        'tenant_form': tenant_form,
        'contract_form': contract_form
    })

@login_required(login_url='login')
def manage_contracts(request):
    user_contracts = Contract.objects.filter(house__owner=request.user).select_related('house', 'renter').order_by('-created_at')
    return render(request, 'quanly/dashboard/manage_contracts.html', {'user_contracts': user_contracts})

@login_required(login_url='login')
def manage_tenants(request):
    user_tenants = Tenant.objects.filter(created_by=request.user).prefetch_related('signed_contracts__house').order_by('-created_at')
    return render(request, 'quanly/dashboard/manage_tenants.html', {'user_tenants': user_tenants})
