from django.contrib.auth.decorators import user_passes_test
from contracts.models import Contract, Tenant
from custom_admin.views.helpers import _is_admin_user, _custom_admin_model_list

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_tenants(request):
    return _custom_admin_model_list(
        request, Tenant.objects.select_related('created_by'), 'Quản lý khách thuê (Chỉ xem)', None,
        ['Họ tên', 'SĐT', 'CCCD', 'Giới tính', 'Quản lý bởi'],
        {
            'search': lambda qs, q: qs.filter(full_name__icontains=q),
            'order_by': '-created_at',
            'columns': lambda obj: [
                obj.full_name, obj.phone, obj.cccd,
                obj.get_gender_display(),
                obj.created_by.username if obj.created_by else '-'
            ],
        },
        None, None
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_contracts(request):
    return _custom_admin_model_list(
        request, Contract.objects.select_related('house', 'renter'), 'Quản lý hợp đồng (Chỉ xem)', None,
        ['Khách thuê', 'Nhà', 'Bắt đầu', 'Kết thúc', 'Giá trị', 'Trạng thái'],
        {
            'search': lambda qs, q: qs.filter(renter__full_name__icontains=q),
            'order_by': '-created_at',
            'columns': lambda obj: [
                obj.renter.full_name if obj.renter else '-', obj.house.name if obj.house else '-', 
                obj.start_date.strftime('%d/%m/%Y') if obj.start_date else '-', 
                obj.end_date.strftime('%d/%m/%Y') if obj.end_date else '-', 
                f"{obj.total_value:,} VNĐ" if obj.total_value else '-',
                obj.get_status_display()
            ],
        },
        None, None
    )
