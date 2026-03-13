from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from quanly.models import House, Contract, Furniture, HouseImage, Tenant
from quanly.forms_admin import (
    AdminUserCreateForm, AdminUserUpdateForm, AdminHouseForm,
    AdminFurnitureForm
)

User = get_user_model()

def _is_admin_user(user):
    """
    Helper kiểm tra quyền admin.
    - Chỉ dùng is_superuser (không dùng is_staff).
    - Được tái sử dụng bởi decorator user_passes_test ở hầu hết view admin.
    """
    return user.is_authenticated and user.is_superuser

def custom_admin_login(request):
    """
    Trang đăng nhập riêng cho khu vực custom-admin.

    Luồng chính:
    1) Nếu đã đăng nhập và có quyền admin -> chuyển thẳng dashboard.
    2) Nếu POST -> lấy username/password từ form, gọi authenticate() của Django.
    3) Nếu hợp lệ + có quyền -> login() (Django built-in) để tạo session.
    4) Nếu sai -> trả thông báo lỗi ra template.
    """
    # Nếu đã đăng nhập và là admin, chuyển hướng đến dashboard
    if _is_admin_user(request.user):
        return redirect('custom_admin_dashboard')
    # Xử lý đăng nhập
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
    """
    Đăng xuất tài khoản admin hiện tại.
    - logout() là hàm mặc định của Django Auth.
    - user_passes_test đảm bảo chỉ user đủ quyền mới vào được view này.
    """
    logout(request)
    return redirect('custom_admin_login')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_dashboard(request):
    """
    Dashboard tổng quan cho admin.

    context gồm:
    - total_users/total_houses/total_contracts/pending_houses: số liệu đếm nhanh.
    - latest_users/latest_houses: 5 bản ghi mới nhất để hiển thị.
    """
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
    """
    Hàm helper dựng trang LIST dùng chung cho nhiều model (User/House/...).

    Ý nghĩa tham số:
    - queryset: tập dữ liệu gốc (Django QuerySet) cho module hiện tại.
    - page_title: tiêu đề trang.
    - create_url: tên route dùng cho nút "Tạo mới" (None nếu không cho tạo).
    - headers: danh sách tiêu đề cột của bảng.
    - row_builder: dict cấu hình cách search/sort/render từng dòng.
    - edit_url_name/delete_url_name: tên route cho Sửa/Xóa (None nếu không cho).
    """
    # 1) Lấy từ khóa tìm kiếm từ query string (?q=...)
    query = request.GET.get('q', '').strip()

    # 2) data là biến làm việc trung gian; bắt đầu từ dữ liệu gốc
    data = queryset

    # 3) Nếu người dùng nhập q thì gọi hàm search do từng module cung cấp
    if query:
        data = row_builder['search'](data, query)

    # 4) Sắp xếp theo cấu hình, mặc định bản ghi mới trước
    items = data.order_by(row_builder.get('order_by', '-id'))

    # 5) Chuẩn hóa dữ liệu từng object về dạng rows để template list.html render thống nhất
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
    """
    Helper dựng trang FORM dùng chung cho Create/Edit.
    """
    # Xác định form có upload file/image không để bật enctype multipart/form-data
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
    """
    Helper xóa bản ghi dùng chung.
    - @require_POST: chỉ cho phép HTTP POST để tăng an toàn.
    - guard_self_user=True dùng cho User để chặn tự xóa chính mình.
    """
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
    """
    Trang danh sách User.
    - Search theo username.
    - Sort theo ngày tham gia mới nhất.
    """
    return _custom_admin_model_list(
        request, User.objects.all(), 'Quản lý người dùng', 'custom_admin_user_create',
        ['Username', 'Email', 'Vai trò', 'Trạng thái', 'Ngày tạo'],
        {
            'search': lambda qs, q: qs.filter(username__icontains=q),
            'order_by': '-date_joined',
            'columns': lambda obj: [
                obj.username, obj.email,
                "Quản trị" if obj.is_superuser else "Người dùng",
                "Hoạt động" if obj.is_active else "Khóa",
                obj.date_joined.strftime('%d/%m/%Y %H:%M')
            ]
        },
        'custom_admin_user_edit', 'custom_admin_user_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_user_create(request):
    """Trang tạo mới User."""
    return _custom_admin_model_form(request, AdminUserCreateForm, None, 'Thêm người dùng mới', 'custom_admin_users', 'Tạo tài khoản thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_user_edit(request, user_id):
    """Trang chỉnh sửa User."""
    user = get_object_or_404(User, id=user_id)
    return _custom_admin_model_form(request, AdminUserUpdateForm, user, f'Chỉnh sửa người dùng: {user.username}', 'custom_admin_users', 'Cập nhật tài khoản thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_user_delete(request, user_id):
    """Xóa User theo user_id. Chặn tự xóa chính mình."""
    return _custom_admin_model_delete(request, User, user_id, 'custom_admin_users', guard_self_user=True)

# --- HOUSES (Admin chỉ Read + Update status + Delete vi phạm, KHÔNG Create) ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_houses(request):
    """
    Trang danh sách House.
    - select_related('owner') để tối ưu.
    - Có extra action "Duyệt" khi status=pending.
    - Có extra action "Từ chối" khi status=pending.
    """
    return _custom_admin_model_list(
        request, House.objects.select_related('owner'), 'Quản lý nhà', None,
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
                },
                {
                    'url_name': 'custom_admin_house_reject',
                    'label': 'Từ chối',
                    'class_name': 'danger-btn',
                    'confirm': f'Xác nhận từ chối bài đăng: {obj.name}?',
                },
            ] if obj.status == 'pending' else [],
        },
        'custom_admin_house_edit', 'custom_admin_house_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_edit(request, object_id):
    """Trang chỉnh sửa House (admin có thể đổi status, thông tin)."""
    obj = get_object_or_404(House, id=object_id)
    return _custom_admin_model_form(request, AdminHouseForm, obj, 'Chỉnh sửa nhà', 'custom_admin_houses', 'Cập nhật thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_delete(request, object_id):
    """Xóa House vi phạm."""
    return _custom_admin_model_delete(request, House, object_id, 'custom_admin_houses')

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_approve(request, object_id):
    """Duyệt bài đăng House: chuyển status từ pending sang available."""
    house = get_object_or_404(House, id=object_id)
    house.status = 'available'
    house.save()
    messages.success(request, f'Đã duyệt bài đăng: {house.name}')
    return redirect('custom_admin_houses')

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_reject(request, object_id):
    """Từ chối bài đăng House: chuyển status từ pending sang rejected."""
    house = get_object_or_404(House, id=object_id)
    house.status = 'rejected'
    house.save()
    messages.success(request, f'Đã từ chối bài đăng: {house.name}')
    return redirect('custom_admin_houses')

# --- TENANTS (Admin chỉ Read-Only, KHÔNG Create/Update/Delete) ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_tenants(request):
    """
    Trang danh sách Tenant (read-only).
    - Admin chỉ xem để giám sát, không sửa/xóa.
    - select_related('created_by') để tối ưu.
    """
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
        None, None  # Không cho edit/delete
    )

# --- CONTRACTS (Admin chỉ Read-Only, KHÔNG Create/Update/Delete) ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_contracts(request):
    """
    Trang danh sách Contract (read-only).
    - Admin chỉ xem để giám sát, không sửa/xóa.
    """
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
        None, None  # Không cho edit/delete
    )

# --- FURNITURES (Admin CRUD đầy đủ — quản lý danh mục hệ thống) ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_furnitures(request):
    """Trang danh sách Furniture."""
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
    """Trang tạo mới Furniture."""
    return _custom_admin_model_form(request, AdminFurnitureForm, None, 'Thêm nội thất', 'custom_admin_furnitures', 'Tạo nội thất thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_furniture_edit(request, object_id):
    """Trang chỉnh sửa Furniture."""
    obj = get_object_or_404(Furniture, id=object_id)
    return _custom_admin_model_form(request, AdminFurnitureForm, obj, 'Chỉnh sửa nội thất', 'custom_admin_furnitures', 'Cập nhật thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_furniture_delete(request, object_id):
    """Xóa Furniture."""
    return _custom_admin_model_delete(request, Furniture, object_id, 'custom_admin_furnitures')

# --- HOUSE IMAGES (Admin chỉ Read + Delete vi phạm, KHÔNG Create/Edit) ---
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_images(request):
    """
    Trang danh sách HouseImage (chỉ xem + xóa vi phạm).
    """
    return _custom_admin_model_list(
        request, HouseImage.objects.select_related('house'), 'Quản lý ảnh phụ nhà', None,
        ['Thuộc nhà', 'Đường dẫn ảnh'],
        {
            'search': lambda qs, q: qs.filter(house__name__icontains=q),
            'order_by': '-id',
            'columns': lambda obj: [obj.house.name if obj.house else '-', obj.image.url if obj.image else '-'],
        },
        None, 'custom_admin_house_image_delete'  # Chỉ cho delete, không cho edit
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_image_delete(request, object_id):
    """Xóa HouseImage vi phạm."""
    return _custom_admin_model_delete(request, HouseImage, object_id, 'custom_admin_house_images')
