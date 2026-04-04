from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from houses.models import House, HouseImage
from custom_admin.forms import AdminHouseForm
from custom_admin.views.helpers import _is_admin_user, _custom_admin_model_list, _custom_admin_model_form, _custom_admin_model_delete

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_houses(request):
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
            ] if obj.status in ['pending', 'no_coordinates'] else [],
        },
        'custom_admin_house_edit', 'custom_admin_house_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_edit(request, object_id):
    obj = get_object_or_404(House, id=object_id)
    return _custom_admin_model_form(request, AdminHouseForm, obj, 'Chỉnh sửa nhà', 'custom_admin_houses', 'Cập nhật thành công!')

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_delete(request, object_id):
    return _custom_admin_model_delete(request, House, object_id, 'custom_admin_houses')

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_approve(request, object_id):
    house = get_object_or_404(House, id=object_id)

    if house.lat is None or house.lng is None:
        house.status = 'no_coordinates'
        house.requires_coordinates = True
        house.save(update_fields=['status', 'requires_coordinates'])
        messages.error(request, f'Không thể duyệt "{house.name}" vì chưa có tọa độ. Vui lòng nhập kinh độ/vĩ độ trước.')
        return redirect('custom_admin_houses')

    house.status = 'available'
    house.requires_coordinates = False
    house.save(update_fields=['status', 'requires_coordinates'])
    messages.success(request, f'Đã duyệt bài đăng: {house.name}')
    return redirect('custom_admin_houses')

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_reject(request, object_id):
    house = get_object_or_404(House, id=object_id)
    house.status = 'rejected'
    house.save()
    messages.success(request, f'Đã từ chối bài đăng: {house.name}')
    return redirect('custom_admin_houses')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_images(request):
    return _custom_admin_model_list(
        request, HouseImage.objects.select_related('house'), 'Quản lý ảnh phụ nhà', None,
        ['Thuộc nhà', 'Đường dẫn ảnh'],
        {
            'search': lambda qs, q: qs.filter(house__name__icontains=q),
            'order_by': '-id',
            'columns': lambda obj: [obj.house.name if obj.house else '-', obj.image.url if obj.image else '-'],
        },
        None, 'custom_admin_house_image_delete'
    )

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_house_image_delete(request, object_id):
    return _custom_admin_model_delete(request, HouseImage, object_id, 'custom_admin_house_images')
