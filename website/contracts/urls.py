from django.urls import path, include

urlpatterns = [
    path('', include('contracts.urls.landlord')),
]
