from django.urls import path
from custom_admin.views.furnitures import custom_admin_furnitures, custom_admin_furniture_create, custom_admin_furniture_edit, custom_admin_furniture_delete

urlpatterns = [
    path('furnitures/', custom_admin_furnitures, name='custom_admin_furnitures'),
    path('furnitures/create/', custom_admin_furniture_create, name='custom_admin_furniture_create'),
    path('furnitures/<int:object_id>/edit/', custom_admin_furniture_edit, name='custom_admin_furniture_edit'),
    path('furnitures/<int:object_id>/delete/', custom_admin_furniture_delete, name='custom_admin_furniture_delete'),
]
