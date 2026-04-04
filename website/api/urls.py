from django.urls import path
from . import views

urlpatterns = [
    path('houses/', views.api_houses, name='api_houses'),
    path('polygon-search/', views.api_polygon_search, name='api_polygon_search'),
]
