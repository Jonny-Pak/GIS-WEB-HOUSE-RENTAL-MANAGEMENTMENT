from django.urls import path
from houses.views.public import home, map_view, house_detail_view

urlpatterns = [
    path('', home, name='home'),
    path('map/', map_view, name='map_view'),
    path('house-detail/<int:house_id>/', house_detail_view, name='house_detail'),
]
