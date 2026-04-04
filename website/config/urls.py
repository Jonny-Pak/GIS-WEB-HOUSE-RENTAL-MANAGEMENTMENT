"""
URL configuration for House Rental Management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Accounts
    path('auth/', include('accounts.urls.auth')),
    path('auth/', include('accounts.urls.profile')),
    
    # API
    path('api/v1/', include('houses.api.urls')),
    
    # Contracts
    path('contracts/', include('contracts.urls.landlord')),
    
    # Custom Admin
    path('custom-admin/', include('custom_admin.urls.auth')),
    path('custom-admin/', include('custom_admin.urls.users')),
    path('custom-admin/', include('custom_admin.urls.houses')),
    path('custom-admin/', include('custom_admin.urls.contracts')),
    path('custom-admin/', include('custom_admin.urls.furnitures')),
    
    # Houses
    path('', include('houses.urls.public')),
    path('', include('houses.urls.landlord')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
