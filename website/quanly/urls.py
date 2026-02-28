from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='quanly/accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('detail/<int:house_id>/', views.house_detail, name='house_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('post-house/', views.post_house, name='post_house'),
    path('manage_post/', views.manage_post, name='manage_post'),
    path('manage-contracts/', views.manage_contracts, name='manage_contracts'),
    path('dashboard/house/<int:house_id>/contract/new/', views.create_contract, name='create_contract'),
    path('custom-admin/login/', views.custom_admin_login, name='custom_admin_login'),
    path('custom-admin/logout/', views.custom_admin_logout, name='custom_admin_logout'),
    path('custom-admin/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    
    path('custom-admin/users/', views.custom_admin_users, name='custom_admin_users'),
    path('custom-admin/users/create/', views.custom_admin_user_create, name='custom_admin_user_create'),
    path('custom-admin/users/<int:user_id>/edit/', views.custom_admin_user_edit, name='custom_admin_user_edit'),
    path('custom-admin/users/<int:user_id>/delete/', views.custom_admin_user_delete, name='custom_admin_user_delete'),

    path('custom-admin/groups/', views.custom_admin_groups, name='custom_admin_groups'),
    path('custom-admin/groups/create/', views.custom_admin_group_create, name='custom_admin_group_create'),
    path('custom-admin/groups/<int:object_id>/edit/', views.custom_admin_group_edit, name='custom_admin_group_edit'),
    path('custom-admin/groups/<int:object_id>/delete/', views.custom_admin_group_delete, name='custom_admin_group_delete'),

    path('custom-admin/houses/', views.custom_admin_houses, name='custom_admin_houses'),
    path('custom-admin/houses/create/', views.custom_admin_house_create, name='custom_admin_house_create'),
    path('custom-admin/houses/<int:object_id>/edit/', views.custom_admin_house_edit, name='custom_admin_house_edit'),
    path('custom-admin/houses/<int:object_id>/delete/', views.custom_admin_house_delete, name='custom_admin_house_delete'),
    path('custom-admin/houses/<int:object_id>/approve/', views.custom_admin_house_approve, name='custom_admin_house_approve'),

    path('custom-admin/contracts/', views.custom_admin_contracts, name='custom_admin_contracts'),
    path('custom-admin/contracts/create/', views.custom_admin_contract_create, name='custom_admin_contract_create'),
    path('custom-admin/contracts/<int:object_id>/edit/', views.custom_admin_contract_edit, name='custom_admin_contract_edit'),
    path('custom-admin/contracts/<int:object_id>/delete/', views.custom_admin_contract_delete, name='custom_admin_contract_delete'),

    path('custom-admin/furnitures/', views.custom_admin_furnitures, name='custom_admin_furnitures'),
    path('custom-admin/furnitures/create/', views.custom_admin_furniture_create, name='custom_admin_furniture_create'),
    path('custom-admin/furnitures/<int:object_id>/edit/', views.custom_admin_furniture_edit, name='custom_admin_furniture_edit'),
    path('custom-admin/furnitures/<int:object_id>/delete/', views.custom_admin_furniture_delete, name='custom_admin_furniture_delete'),

    path('custom-admin/house-images/', views.custom_admin_house_images, name='custom_admin_house_images'),
    path('custom-admin/house-images/create/', views.custom_admin_house_image_create, name='custom_admin_house_image_create'),
    path('custom-admin/house-images/<int:object_id>/edit/', views.custom_admin_house_image_edit, name='custom_admin_house_image_edit'),
    path('custom-admin/house-images/<int:object_id>/delete/', views.custom_admin_house_image_delete, name='custom_admin_house_image_delete'),
]