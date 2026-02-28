from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from quanly.models import House, Contract, Furniture, HouseImage, Tenant
from quanly.forms_admin import (
    AdminUserCreateForm, AdminUserUpdateForm, AdminHouseForm,
    AdminFurnitureForm, AdminContractForm, AdminHouseImageForm, AdminGroupForm
)

User = get_user_model()

def _is_admin_user(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

def custom_admin_login(request):
    if _is_admin_user(request.user):
        return redirect('custom_admin_dashboard')

    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and _is_admin_user(user):
            login(request, user)
            return redirect('custom_admin_dashboard')
        else:
            error_message = 'Tài khoản hoặc mật khẩu không đúng, hoặc bạn không có quyền.'

    return render(request, 'quanly/custom_admin/login.html', {'error': error_message})

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_logout(request):
    logout(request)
    return redirect('custom_admin_login')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_houses': House.objects.count(),
        'total_contracts': Contract.objects.count(),
        'pending_houses': House.objects.filter(status='pending').count(),
        'latest_users': User.objects.order_by('-date_joined')[:5],
        'latest_houses': House.objects.order_by('-created_at')[:5],
    }
    return render(request, 'quanly/custom_admin/dashboard.html', context)

# --- GENERIC HELPERS ---
def _custom_admin_model_list(request, queryset, page_title, create_url, headers, row_builder, edit_url_name, delete_url_name):
    query = request.GET.get('q', '').strip()
    data = queryset
    if query:
        data = row_builder['search'](data, query)

    items = data.order_by(row_builder.get('order_by', '-id'))
    rows = [
        {
            'id': item.id,
            'columns': row_builder['columns'](item),
            'extra_actions': row_builder.get('extra_actions', lambda obj: [])(item),
        }
        for item in items
    ]

    return render(request, 'quanly/custom_admin/list.html', {
        'page_title': page_title,
        'create_url': create_url,
        'items': items,
        'query': query,
        'headers': headers,
        'rows': rows,
        'edit_url_name': edit_url_name,
        'delete_url_name': delete_url_name,
    })

def _custom_admin_model_form(request, form_class, instance, page_title, back_url, success_message):
    is_multipart = getattr(form_class.Meta, 'is_multipart', False)
    if 'request.FILES' in str(form_class): # Simple heuristic if images are involved
        is_multipart = True
    else:
        # Check if form has ImageField or FileField
        for field in dict(form_class.base_fields).values():
            if type(field).__name__ in ['ImageField', 'FileField']:
                is_multipart = True

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES if is_multipart else None, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, success_message)
            return redirect(back_url)
    else:
        form = form_class(instance=instance)

    return render(request, 'quanly/custom_admin/form.html', {
        'page_title': page_title,
        'form': form,
        'back_url': back_url,
        'is_multipart': is_multipart,
    })

@require_POST
def _custom_admin_model_delete(request, model, object_id, back_url, guard_self_user=False):
    obj = get_object_or_404(model, id=object_id)
    if guard_self_user and obj.id == request.user.id:
        messages.error(request, 'Bạn không thể tự xóa tài khoản của chính mình.')
    else:
        obj.delete()
        messages.success(request, 'Xóa dữ liệu thành công.')
    return redirect(back_url)

# --- USERS ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_users(request):
    return _custom_admin_model_list(
        request, User.objects.all(), 'Quản lý người dùng', 'custom_admin_user_create',
        ['Username', 'Email', 'Vai trò', 'Trạng thái', 'Ngày tạo'],
        {
            'search': lambda qs, q: qs.filter(username__icontains=q),
            'order_by': '-date_joined',
            'columns': lambda obj: [
                obj.username, obj.email,
                "Quản trị" if obj.is_superuser else ("Nhân viên" if obj.is_staff else "Khách hàng"),
                "Hoạt động" if obj.is_active else "Khóa",
                obj.date_joined.strftime('%d/%m/%Y %H:%M')
            ]
        },
        'custom_admin_user_edit', 'custom_admin_user_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_user_create(request):
    return _custom_admin_model_form(request, AdminUserCreateForm, None, 'Thêm người dùng mới', 'custom_admin_users', 'Tạo tài khoản thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return _custom_admin_model_form(request, AdminUserUpdateForm, user, f'Chỉnh sửa người dùng: {user.username}', 'custom_admin_users', 'Cập nhật tài khoản thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_user_delete(request, user_id):
    return _custom_admin_model_delete(request, User, user_id, 'custom_admin_users', guard_self_user=True)

# --- GROUPS ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_groups(request):
    return _custom_admin_model_list(
        request, Group.objects.all(), 'Quản lý nhóm quyền', 'custom_admin_group_create',
        ['Tên nhóm', 'Số lượng User'],
        {
            'search': lambda qs, q: qs.filter(name__icontains=q),
            'order_by': 'name',
            'columns': lambda obj: [obj.name, obj.user_set.count()]
        },
        'custom_admin_group_edit', 'custom_admin_group_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_group_create(request):
    return _custom_admin_model_form(request, AdminGroupForm, None, 'Thêm nhóm', 'custom_admin_groups', 'Tạo nhóm thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_group_edit(request, object_id):
    obj = get_object_or_404(Group, id=object_id)
    return _custom_admin_model_form(request, AdminGroupForm, obj, 'Chỉnh sửa nhóm', 'custom_admin_groups', 'Cập nhật thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_group_delete(request, object_id):
    return _custom_admin_model_delete(request, Group, object_id, 'custom_admin_groups')

# --- HOUSES ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_houses(request):
    return _custom_admin_model_list(
        request, House.objects.select_related('owner'), 'Quản lý nhà', 'custom_admin_house_create',
        ['Tên nhà', 'Chủ nhà', 'Quận', 'Trạng thái', 'Giá'],
        {
            'search': lambda qs, q: qs.filter(name__icontains=q),
            'order_by': '-created_at',
            'columns': lambda obj: [
                obj.name, obj.owner.username if obj.owner else '-', 
                obj.get_district_display(), obj.get_status_display(), f"{obj.price:,} VNĐ" if obj.price else 'Thỏa thuận'
            ],
            'extra_actions': lambda obj: [
                {
                    'url_name': 'custom_admin_house_approve',
                    'label': 'Duyệt',
                    'class_name': 'success-btn',
                    'confirm': f'Xác nhận duyệt bài đăng: {obj.name}?',
                }
            ] if obj.status == 'pending' else [],
        },
        'custom_admin_house_edit', 'custom_admin_house_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_create(request):
    return _custom_admin_model_form(request, AdminHouseForm, None, 'Thêm nhà', 'custom_admin_houses', 'Tạo nhà thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_edit(request, object_id):
    obj = get_object_or_404(House, id=object_id)
    return _custom_admin_model_form(request, AdminHouseForm, obj, 'Chỉnh sửa nhà', 'custom_admin_houses', 'Cập nhật thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_delete(request, object_id):
    return _custom_admin_model_delete(request, House, object_id, 'custom_admin_houses')

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_approve(request, object_id):
    house = get_object_or_404(House, id=object_id)
    house.status = 'available'
    house.save()
    messages.success(request, f'Đã duyệt bài đăng: {house.name}')
    return redirect('custom_admin_houses')

# --- CONTRACTS ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_contracts(request):
    return _custom_admin_model_list(
        request, Contract.objects.select_related('house', 'renter'), 'Quản lý hợp đồng', 'custom_admin_contract_create',
        ['Khách thuê', 'Nhà', 'Bắt đầu', 'Kết thúc', 'Giá trị'],
        {
            'search': lambda qs, q: qs.filter(renter__full_name__icontains=q),
            'order_by': '-created_at',
            'columns': lambda obj: [
                obj.renter.full_name if obj.renter else '-', obj.house.name if obj.house else '-', 
                obj.start_date.strftime('%d/%m/%Y') if obj.start_date else '-', 
                obj.end_date.strftime('%d/%m/%Y') if obj.end_date else '-', 
                f"{obj.total_value:,} VNĐ" if obj.total_value else '-'
            ],
        },
        'custom_admin_contract_edit', 'custom_admin_contract_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_contract_create(request):
    return _custom_admin_model_form(request, AdminContractForm, None, 'Thêm hợp đồng', 'custom_admin_contracts', 'Tạo hợp đồng thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_contract_edit(request, object_id):
    obj = get_object_or_404(Contract, id=object_id)
    return _custom_admin_model_form(request, AdminContractForm, obj, 'Chỉnh sửa hợp đồng', 'custom_admin_contracts', 'Cập nhật thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_contract_delete(request, object_id):
    return _custom_admin_model_delete(request, Contract, object_id, 'custom_admin_contracts')

# --- FURNITURES ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_furnitures(request):
    return _custom_admin_model_list(
        request, Furniture.objects.all(), 'Quản lý nội thất', 'custom_admin_furniture_create',
        ['Tên nội thất'],
        {
            'search': lambda qs, q: qs.filter(name__icontains=q),
            'order_by': 'name',
            'columns': lambda obj: [obj.name],
        },
        'custom_admin_furniture_edit', 'custom_admin_furniture_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_furniture_create(request):
    return _custom_admin_model_form(request, AdminFurnitureForm, None, 'Thêm nội thất', 'custom_admin_furnitures', 'Tạo nội thất thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_furniture_edit(request, object_id):
    obj = get_object_or_404(Furniture, id=object_id)
    return _custom_admin_model_form(request, AdminFurnitureForm, obj, 'Chỉnh sửa nội thất', 'custom_admin_furnitures', 'Cập nhật thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_furniture_delete(request, object_id):
    return _custom_admin_model_delete(request, Furniture, object_id, 'custom_admin_furnitures')

# --- HOUSE IMAGES ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_images(request):
    return _custom_admin_model_list(
        request, HouseImage.objects.select_related('house'), 'Quản lý ảnh phụ nhà', 'custom_admin_house_image_create',
        ['Thuộc nhà', 'Đường dẫn ảnh'],
        {
            'search': lambda qs, q: qs.filter(house__name__icontains=q),
            'order_by': '-id',
            'columns': lambda obj: [obj.house.name if obj.house else '-', obj.image.url if obj.image else '-'],
        },
        'custom_admin_house_image_edit', 'custom_admin_house_image_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_image_create(request):
    return _custom_admin_model_form(request, AdminHouseImageForm, None, 'Thêm ảnh phụ', 'custom_admin_house_images', 'Đã thêm ảnh!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_image_edit(request, object_id):
    obj = get_object_or_404(HouseImage, id=object_id)
    return _custom_admin_model_form(request, AdminHouseImageForm, obj, 'Chỉnh sửa ảnh phụ', 'custom_admin_house_images', 'Cập nhật thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_image_delete(request, object_id):
    return _custom_admin_model_delete(request, HouseImage, object_id, 'custom_admin_house_images')
