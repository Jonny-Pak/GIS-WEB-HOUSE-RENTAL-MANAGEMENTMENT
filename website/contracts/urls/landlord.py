from django.urls import path
from contracts.views.landlord import manage_contracts, manage_tenants, create_contract, edit_contract, terminate_contract, edit_tenant

urlpatterns = [
    path('manage-contracts/', manage_contracts, name='manage_contracts'),
    path('manage-tenants/', manage_tenants, name='manage_tenants'),
    path('dashboard/house/<int:house_id>/contract/new/', create_contract, name='create_contract'),
    path('dashboard/contract/edit/<int:contract_id>/', edit_contract, name='edit_contract'),
    path('dashboard/contract/terminate/<int:contract_id>/', terminate_contract, name='terminate_contract'),
    path('dashboard/tenant/edit/<int:tenant_id>/', edit_tenant, name='edit_tenant'),
]
