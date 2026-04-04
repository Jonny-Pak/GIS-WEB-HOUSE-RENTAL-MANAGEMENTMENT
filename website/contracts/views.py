from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Tenant, Contract
from houses.models import House
from .forms import TenantForm, ContractForm

@login_required(login_url='login')
def create_contract(request, house_id):
    house = get_object_or_404(House, id=house_id, owner=request.user)
    if house.status == 'rented':
        messages.error(request, 'Căn nhà này đã được cho thuê, không thể tạo thêm hợp đồng.')
        return redirect('manage_post')
    if request.method == 'POST':
        tenant_form = TenantForm(request.POST, request.FILES)
        contract_form = ContractForm(request.POST, request.FILES)
        if tenant_form.is_valid() and contract_form.is_valid():
            tenant = tenant_form.save(commit=False)
            tenant.created_by = request.user
            tenant.save()
            contract = contract_form.save(commit=False)
            contract.house = house
            contract.renter = tenant
            contract.status = 'active'
            contract.save()
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
