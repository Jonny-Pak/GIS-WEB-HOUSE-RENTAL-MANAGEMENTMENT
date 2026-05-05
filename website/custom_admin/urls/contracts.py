from django.urls import path
from custom_admin.views.contracts import custom_admin_tenants, custom_admin_contracts

urlpatterns = [
    path('tenants/', custom_admin_tenants, name='custom_admin_tenants'),
    path('contracts/', custom_admin_contracts, name='custom_admin_contracts'),
]
