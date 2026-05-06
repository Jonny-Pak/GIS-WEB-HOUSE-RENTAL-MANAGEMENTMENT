from django.urls import path
from custom_admin.views.pages import custom_admin_pages, custom_admin_page_create, custom_admin_page_edit, custom_admin_page_delete

urlpatterns = [
    path('pages/', custom_admin_pages, name='custom_admin_pages'),
    path('pages/create/', custom_admin_page_create, name='custom_admin_page_create'),
    path('pages/<int:object_id>/edit/', custom_admin_page_edit, name='custom_admin_page_edit'),
    path('pages/<int:object_id>/delete/', custom_admin_page_delete, name='custom_admin_page_delete'),
]
