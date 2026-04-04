from django.urls import path, include

urlpatterns = [
    path('', include('custom_admin.urls.auth')),
    path('', include('custom_admin.urls.users')),
    path('', include('custom_admin.urls.houses')),
    path('', include('custom_admin.urls.contracts')),
    path('', include('custom_admin.urls.furnitures')),
]
