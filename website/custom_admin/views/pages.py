from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from houses.models import StaticPage
from custom_admin.forms import AdminStaticPageForm
from custom_admin.views.helpers import _is_admin_user, _custom_admin_model_list, _custom_admin_model_form, _custom_admin_model_delete

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_pages(request):
    return _custom_admin_model_list(
        request, StaticPage.objects.all(), 'Quản lý trang tĩnh', 'custom_admin_page_create',
        ['Mã trang', 'Tiêu đề', 'Cập nhật lần cuối'],
        {
            'search': lambda qs, q: qs.filter(title__icontains=q),
            'order_by': 'slug',
            'columns': lambda obj: [
                obj.get_slug_display(), obj.title, obj.updated_at.strftime("%d/%m/%Y %H:%M")
            ],
        },
        'custom_admin_page_edit', 'custom_admin_page_delete'
    )

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_page_create(request):
    return _custom_admin_model_form(request, AdminStaticPageForm, None, 'Thêm trang tĩnh', 'custom_admin_pages', 'Thêm mới thành công!')

@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_page_edit(request, object_id):
    obj = StaticPage.objects.get(id=object_id)
    return _custom_admin_model_form(request, AdminStaticPageForm, obj, 'Chỉnh sửa trang tĩnh', 'custom_admin_pages', 'Cập nhật thành công!')

@require_POST
@user_passes_test(_is_admin_user, login_url='custom_admin_login')
def custom_admin_page_delete(request, object_id):
    return _custom_admin_model_delete(request, StaticPage, object_id, 'custom_admin_pages')
