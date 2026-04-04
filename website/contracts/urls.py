from django.urls import path
from . import views

urlpatterns = [
    path('manage-contracts/', views.manage_contracts, name='manage_contracts'),
    path('manage-tenants/', views.manage_tenants, name='manage_tenants'),
    path('dashboard/house/<int:house_id>/contract/new/', views.create_contract, name='create_contract'),
]
