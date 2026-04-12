from django.urls import path
from houses.views.landlord import (
    dashboard,
    post_house,
    manage_post,
    edit_house,
    delete_house_view,
    geocode_preview,
)

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('post-house/', post_house, name='post_house'),
    path('dashboard/geocode-preview/', geocode_preview, name='geocode_preview'),
    path('manage_post/', manage_post, name='manage_post'),
    path('dashboard/house/<int:house_id>/edit/', edit_house, name='edit_house'),
    path('dashboard/house/<int:house_id>/delete/', delete_house_view, name='delete_house'),
]

