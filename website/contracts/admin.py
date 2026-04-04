from django.contrib import admin
from .models import Contract, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'cccd', 'gender', 'created_by')
    search_fields = ('full_name', 'phone', 'cccd')
    list_filter = ('gender',)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('renter', 'house', 'start_date', 'end_date', 'total_value', 'status')
    search_fields = ('renter__full_name', 'renter__phone', 'house__name')
    list_filter = ('status',)
    filter_horizontal = ('roommates',)
