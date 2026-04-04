from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from houses.models import Furniture
from custom_admin.forms import AdminFurnitureForm
from custom_admin.views.helpers import _is_admin_user, _custom_admin_model_list, _custom_admin_model_form, _custom_admin_model_delete

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

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_furniture_delete(request, object_id):
    return _custom_admin_model_delete(request, Furniture, object_id, 'custom_admin_furnitures')
