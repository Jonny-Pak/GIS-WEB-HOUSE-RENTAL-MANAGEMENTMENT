from django.urls import path
from . import views
from .views import public
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='quanly/accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('map/', views.map_view, name='map_view'),
    path('house-detail/<int:house_id>/', public.house_detail_view, name='house_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('post-house/', views.post_house, name='post_house'),
    path('manage_post/', views.manage_post, name='manage_post'),
    path('dashboard/house/<int:house_id>/edit/', views.edit_house, name='edit_house'),
    path('dashboard/house/<int:house_id>/delete/', views.delete_house, name='delete_house'),
    path('manage-contracts/', views.manage_contracts, name='manage_contracts'),
    path('manage-tenants/', views.manage_tenants, name='manage_tenants'),
    path('dashboard/house/<int:house_id>/contract/new/', views.create_contract, name='create_contract'),
    path('custom-admin/login/', views.custom_admin_login, name='custom_admin_login'),
    path('custom-admin/logout/', views.custom_admin_logout, name='custom_admin_logout'),
    path('custom-admin/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # --- Custom Admin: Users (CRUD đầy đủ) ---
    path('custom-admin/users/', views.custom_admin_users, name='custom_admin_users'),
    path('custom-admin/users/create/', views.custom_admin_user_create, name='custom_admin_user_create'),
    path('custom-admin/users/<int:user_id>/edit/', views.custom_admin_user_edit, name='custom_admin_user_edit'),
    path('custom-admin/users/<int:user_id>/delete/', views.custom_admin_user_delete, name='custom_admin_user_delete'),

    # --- Custom Admin: Houses (Read + Update + Delete + Approve/Reject, KHÔNG Create) ---
    path('custom-admin/houses/', views.custom_admin_houses, name='custom_admin_houses'),
    path('custom-admin/houses/<int:object_id>/edit/', views.custom_admin_house_edit, name='custom_admin_house_edit'),
    path('custom-admin/houses/<int:object_id>/delete/', views.custom_admin_house_delete, name='custom_admin_house_delete'),
    path('custom-admin/houses/<int:object_id>/approve/', views.custom_admin_house_approve, name='custom_admin_house_approve'),
    path('custom-admin/houses/<int:object_id>/reject/', views.custom_admin_house_reject, name='custom_admin_house_reject'),

    # --- Custom Admin: Tenants (Read-Only) ---
    path('custom-admin/tenants/', views.custom_admin_tenants, name='custom_admin_tenants'),

    # --- Custom Admin: Contracts (Read-Only) ---
    path('custom-admin/contracts/', views.custom_admin_contracts, name='custom_admin_contracts'),

    # --- Custom Admin: Furnitures (CRUD đầy đủ — danh mục hệ thống) ---
    path('custom-admin/furnitures/', views.custom_admin_furnitures, name='custom_admin_furnitures'),
    path('custom-admin/furnitures/create/', views.custom_admin_furniture_create, name='custom_admin_furniture_create'),
    path('custom-admin/furnitures/<int:object_id>/edit/', views.custom_admin_furniture_edit, name='custom_admin_furniture_edit'),
    path('custom-admin/furnitures/<int:object_id>/delete/', views.custom_admin_furniture_delete, name='custom_admin_furniture_delete'),

    # --- Custom Admin: House Images (Read + Delete vi phạm) ---
    path('custom-admin/house-images/', views.custom_admin_house_images, name='custom_admin_house_images'),
    path('custom-admin/house-images/<int:object_id>/delete/', views.custom_admin_house_image_delete, name='custom_admin_house_image_delete'),
]