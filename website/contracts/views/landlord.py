from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from contracts.models import Tenant, Contract
from houses.models import House
from contracts.forms import TenantForm, ContractForm
from contracts.services.contract_service import create_contract_workflow

@login_required(login_url='login')
def create_contract(request, house_id):
    house = get_object_or_404(House, id=house_id, owner=request.user)
    if house.status == 'rented':
        messages.error(request, 'Căn nhà này đã được cho thuê, không thể tạo thêm hợp đồng.')
        return redirect('manage_post')

    existing_tenants = Tenant.objects.filter(created_by=request.user).order_by('full_name')

    if request.method == 'POST':
        tenant_form = TenantForm(request.POST, request.FILES)
        contract_form = ContractForm(request.POST, request.FILES)
        if tenant_form.is_valid() and contract_form.is_valid():
            try:
                create_contract_workflow(house, request.user, tenant_form, contract_form)
                messages.success(request, f'Đã tạo hợp đồng thành công cho căn nhà: {house.name}!')
                return redirect('manage_post')
            except Exception as e:
                messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin biểu mẫu.')
    else:
        tenant_form = TenantForm()
        contract_form = ContractForm()
    return render(request, 'dashboard/create_contract.html', {
        'house': house,
        'tenant_form': tenant_form,
        'contract_form': contract_form,
        'existing_tenants': existing_tenants
    })

@login_required(login_url='login')
def manage_contracts(request):
    from django.db.models import Sum, Q
    from datetime import date, timedelta
    
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    
    user_contracts = Contract.objects.filter(house__owner=request.user).select_related('house', 'renter')
    
    if query:
        user_contracts = user_contracts.filter(
            Q(house__name__icontains=query) | 
            Q(renter__full_name__icontains=query) | 
            Q(renter__phone__icontains=query)
        )
    
    if status:
        user_contracts = user_contracts.filter(status=status)

    user_contracts = user_contracts.order_by('-created_at')
    
    # Tính toán số liệu Dashboard (Dựa trên tất cả hợp đồng của user, không bị ảnh hưởng bởi filter search)
    all_active_contracts = Contract.objects.filter(house__owner=request.user, status='active')
    today = date.today()
    next_30_days = today + timedelta(days=30)
    
    total_active = all_active_contracts.count()
    total_revenue = all_active_contracts.aggregate(total=Sum('total_value'))['total'] or 0
    expiring_soon = all_active_contracts.filter(end_date__lte=next_30_days, end_date__gte=today).count()
    
    # Phân trang: 10 hợp đồng mỗi trang
    paginator = Paginator(user_contracts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/manage_contracts.html', {
        'page_obj': page_obj,
        'user_contracts': page_obj,
        'total_active': total_active,
        'total_revenue': total_revenue,
        'expiring_soon': expiring_soon,
        'query': query,
        'selected_status': status
    })

@login_required(login_url='login')
def manage_tenants(request):
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    
    user_tenants = Tenant.objects.filter(created_by=request.user).prefetch_related('signed_contracts__house')
    
    if query:
        user_tenants = user_tenants.filter(
            Q(full_name__icontains=query) | 
            Q(phone__icontains=query) | 
            Q(cccd__icontains=query)
        )
        
    user_tenants = user_tenants.order_by('-created_at')
    
    # Phân trang: 12 khách thuê mỗi trang
    paginator = Paginator(user_tenants, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/manage_tenants.html', {
        'page_obj': page_obj,
        'user_tenants': page_obj,
        'query': query
    })

@login_required(login_url='login')
def edit_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id, created_by=request.user)
    if request.method == 'POST':
        form = TenantForm(request.POST, request.FILES, instance=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật thông tin khách thuê: {tenant.full_name} thành công.')
            return redirect('manage_tenants')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = TenantForm(instance=tenant)
    
    return render(request, 'dashboard/edit_tenant.html', {
        'tenant': tenant,
        'form': form
    })

@login_required(login_url='login')
def edit_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id, house__owner=request.user)
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật hợp đồng #{contract_id} thành công.')
            return redirect('manage_contracts')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = ContractForm(instance=contract)
    
    return render(request, 'dashboard/edit_contract.html', {
        'contract': contract,
        'form': form
    })

@login_required(login_url='login')
def terminate_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id, house__owner=request.user)
    
    if contract.status != 'active':
        messages.warning(request, 'Hợp đồng này đã kết thúc trước đó.')
        return redirect('manage_contracts')

    # Chấm dứt hợp đồng
    contract.status = 'terminated'
    contract.save()
    
    # Cập nhật trạng thái nhà về còn trống
    if contract.house:
        house = contract.house
        house.status = 'available'
        house.save()
        messages.success(request, f'Đã chấm dứt hợp đồng và cập nhật căn nhà "{house.name}" về trạng thái "Còn trống".')
    else:
        messages.success(request, 'Đã chấm dứt hợp đồng thành công.')
        
    return redirect('manage_contracts')
