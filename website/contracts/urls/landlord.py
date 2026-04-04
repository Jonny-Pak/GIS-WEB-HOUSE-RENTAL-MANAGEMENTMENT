from django.urls import path
from contracts.views.landlord import manage_contracts, manage_tenants, create_contract

urlpatterns = [
    path('manage-contracts/', manage_contracts, name='manage_contracts'),
    path('manage-tenants/', manage_tenants, name='manage_tenants'),
    path('dashboard/house/<int:house_id>/contract/new/', create_contract, name='create_contract'),
]
