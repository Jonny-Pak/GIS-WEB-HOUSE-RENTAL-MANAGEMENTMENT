from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('map/', views.map_view, name='map_view'),
    path('house-detail/<int:house_id>/', views.house_detail_view, name='house_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('post-house/', views.post_house, name='post_house'),
    path('manage_post/', views.manage_post, name='manage_post'),
    path('dashboard/house/<int:house_id>/edit/', views.edit_house, name='edit_house'),
    path('dashboard/house/<int:house_id>/delete/', views.delete_house, name='delete_house'),
]
