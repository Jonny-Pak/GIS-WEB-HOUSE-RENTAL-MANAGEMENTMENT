from django.urls import path
from custom_admin.views.houses import custom_admin_houses, custom_admin_house_edit, custom_admin_house_delete, custom_admin_house_approve, custom_admin_house_reject, custom_admin_house_images, custom_admin_house_image_delete

urlpatterns = [
    path('houses/', custom_admin_houses, name='custom_admin_houses'),
    path('houses/<int:object_id>/edit/', custom_admin_house_edit, name='custom_admin_house_edit'),
    path('houses/<int:object_id>/delete/', custom_admin_house_delete, name='custom_admin_house_delete'),
    path('houses/<int:object_id>/approve/', custom_admin_house_approve, name='custom_admin_house_approve'),
    path('houses/<int:object_id>/reject/', custom_admin_house_reject, name='custom_admin_house_reject'),

    path('house-images/', custom_admin_house_images, name='custom_admin_house_images'),
    path('house-images/<int:object_id>/delete/', custom_admin_house_image_delete, name='custom_admin_house_image_delete'),
]
