from django.urls import path, include

urlpatterns = [
    path('', include('houses.urls.public')),
    path('', include('houses.urls.landlord')),
]
