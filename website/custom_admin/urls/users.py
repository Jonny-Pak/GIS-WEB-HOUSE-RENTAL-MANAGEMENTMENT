from django.urls import path
from custom_admin.views.users import custom_admin_users, custom_admin_user_create, custom_admin_user_edit, custom_admin_user_delete

urlpatterns = [
    path('users/', custom_admin_users, name='custom_admin_users'),
    path('users/create/', custom_admin_user_create, name='custom_admin_user_create'),
    path('users/<int:user_id>/edit/', custom_admin_user_edit, name='custom_admin_user_edit'),
    path('users/<int:user_id>/delete/', custom_admin_user_delete, name='custom_admin_user_delete'),
]
