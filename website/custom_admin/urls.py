from django.urls import path
from . import views

urlpatterns = [
    # --- Auth ---
    path('login/', views.custom_admin_login, name='custom_admin_login'),
    path('logout/', views.custom_admin_logout, name='custom_admin_logout'),
    path('', views.custom_admin_dashboard, name='custom_admin_dashboard'),

    # --- Users (CRUD đầy đủ) ---
    path('users/', views.custom_admin_users, name='custom_admin_users'),
    path('users/create/', views.custom_admin_user_create, name='custom_admin_user_create'),
    path('users/<int:user_id>/edit/', views.custom_admin_user_edit, name='custom_admin_user_edit'),
    path('users/<int:user_id>/delete/', views.custom_admin_user_delete, name='custom_admin_user_delete'),

    # --- Houses (Read + Update + Delete + Approve/Reject) ---
    path('houses/', views.custom_admin_houses, name='custom_admin_houses'),
    path('houses/<int:object_id>/edit/', views.custom_admin_house_edit, name='custom_admin_house_edit'),
    path('houses/<int:object_id>/delete/', views.custom_admin_house_delete, name='custom_admin_house_delete'),
    path('houses/<int:object_id>/approve/', views.custom_admin_house_approve, name='custom_admin_house_approve'),
    path('houses/<int:object_id>/reject/', views.custom_admin_house_reject, name='custom_admin_house_reject'),

    # --- Tenants (Read-Only) ---
    path('tenants/', views.custom_admin_tenants, name='custom_admin_tenants'),

    # --- Contracts (Read-Only) ---
    path('contracts/', views.custom_admin_contracts, name='custom_admin_contracts'),

    # --- Furnitures (CRUD đầy đủ) ---
    path('furnitures/', views.custom_admin_furnitures, name='custom_admin_furnitures'),
    path('furnitures/create/', views.custom_admin_furniture_create, name='custom_admin_furniture_create'),
    path('furnitures/<int:object_id>/edit/', views.custom_admin_furniture_edit, name='custom_admin_furniture_edit'),
    path('furnitures/<int:object_id>/delete/', views.custom_admin_furniture_delete, name='custom_admin_furniture_delete'),

    # --- House Images (Read + Delete) ---
    path('house-images/', views.custom_admin_house_images, name='custom_admin_house_images'),
    path('house-images/<int:object_id>/delete/', views.custom_admin_house_image_delete, name='custom_admin_house_image_delete'),
]
