from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

def _is_admin_user(user):
    """Helper kiểm tra quyền admin."""
    return user.is_authenticated and user.is_superuser

def _custom_admin_model_list(request, queryset, page_title, create_url, headers, row_builder, edit_url_name, delete_url_name):
    query = request.GET.get('q', '').strip()
    data = queryset
    if query:
        data = row_builder['search'](data, query)
    
    # Sắp xếp
    items_all = data.order_by(row_builder.get('order_by', '-id'))
    
    # Phân trang
    paginator = Paginator(items_all, 10) # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    rows = [
        {
            'id': item.id,
            'columns': row_builder['columns'](item),
            'extra_actions': row_builder.get('extra_actions', lambda obj: [])(item),
        }
        for item in page_obj
    ]
    
    return render(request, 'custom_admin/list.html', {
        'page_title': page_title,
        'create_url': create_url,
        'items': page_obj,  # Trả về page_obj để tương thích ngược nếu cần
        'page_obj': page_obj,
        'query': query,
        'headers': headers,
        'rows': rows,
        'edit_url_name': edit_url_name,
        'delete_url_name': delete_url_name,
    })

def _custom_admin_model_form(request, form_class, instance, page_title, back_url, success_message):
    is_multipart = getattr(form_class.Meta, 'is_multipart', False)
    if 'request.FILES' in str(form_class):
        is_multipart = True
    else:
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

    return render(request, 'custom_admin/form.html', {
        'page_title': page_title,
        'form': form,
        'back_url': back_url,
        'is_multipart': is_multipart,
    })

def _custom_admin_model_delete(request, model, object_id, back_url, guard_self_user=False):
    obj = get_object_or_404(model, id=object_id)
    if guard_self_user and obj.id == request.user.id:
        messages.error(request, 'Bạn không thể tự xóa tài khoản của chính mình.')
    else:
        obj.delete()
        messages.success(request, 'Xóa dữ liệu thành công.')
    return redirect(back_url)
