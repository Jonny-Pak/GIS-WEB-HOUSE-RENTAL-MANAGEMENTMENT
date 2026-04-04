from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from custom_admin.forms import AdminUserCreateForm, AdminUserUpdateForm
from custom_admin.views.helpers import _is_admin_user, _custom_admin_model_list, _custom_admin_model_form, _custom_admin_model_delete

User = get_user_model()

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
                "Quản trị" if obj.is_superuser else "Người dùng",
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

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_user_delete(request, user_id):
    return _custom_admin_model_delete(request, User, user_id, 'custom_admin_users', guard_self_user=True)
