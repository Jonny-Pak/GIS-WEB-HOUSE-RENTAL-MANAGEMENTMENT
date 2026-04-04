from django.urls import path
from django.contrib.auth import views as auth_views 
from . import views, views_admin

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='quanly/accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    
    # Custom Admin
    path('custom-admin/login/', views_admin.custom_admin_login, name='custom_admin_login'),
    path('custom-admin/logout/', views_admin.custom_admin_logout, name='custom_admin_logout'),
    path('custom-admin/', views_admin.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('custom-admin/users/', views_admin.custom_admin_users, name='custom_admin_users'),
    path('custom-admin/users/create/', views_admin.custom_admin_user_create, name='custom_admin_user_create'),
    path('custom-admin/users/<int:user_id>/edit/', views_admin.custom_admin_user_edit, name='custom_admin_user_edit'),
    path('custom-admin/users/<int:user_id>/delete/', views_admin.custom_admin_user_delete, name='custom_admin_user_delete'),
    
    path('custom-admin/houses/', views_admin.custom_admin_houses, name='custom_admin_houses'),
    path('custom-admin/houses/<int:object_id>/edit/', views_admin.custom_admin_house_edit, name='custom_admin_house_edit'),
    path('custom-admin/houses/<int:object_id>/delete/', views_admin.custom_admin_house_delete, name='custom_admin_house_delete'),
    path('custom-admin/houses/<int:object_id>/approve/', views_admin.custom_admin_house_approve, name='custom_admin_house_approve'),
    path('custom-admin/houses/<int:object_id>/reject/', views_admin.custom_admin_house_reject, name='custom_admin_house_reject'),

    path('custom-admin/tenants/', views_admin.custom_admin_tenants, name='custom_admin_tenants'),
    path('custom-admin/contracts/', views_admin.custom_admin_contracts, name='custom_admin_contracts'),

    path('custom-admin/furnitures/', views_admin.custom_admin_furnitures, name='custom_admin_furnitures'),
    path('custom-admin/furnitures/create/', views_admin.custom_admin_furniture_create, name='custom_admin_furniture_create'),
    path('custom-admin/furnitures/<int:object_id>/edit/', views_admin.custom_admin_furniture_edit, name='custom_admin_furniture_edit'),
    path('custom-admin/furnitures/<int:object_id>/delete/', views_admin.custom_admin_furniture_delete, name='custom_admin_furniture_delete'),

    path('custom-admin/house-images/', views_admin.custom_admin_house_images, name='custom_admin_house_images'),
    path('custom-admin/house-images/<int:object_id>/delete/', views_admin.custom_admin_house_image_delete, name='custom_admin_house_image_delete'),
]
