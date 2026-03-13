from django.contrib import admin
from .models import House, Furniture, HouseImage, Contract, Tenant, Profile
# Register your models here.

# --- Actions cho House ---
@admin.action(description='Duyệt bài đăng (Đang cho thuê)')
def make_available(modeladmin, request, queryset):
    queryset.update(status='available')

@admin.action(description='Từ chối bài đăng')
def make_rejected(modeladmin, request, queryset):
    queryset.update(status='rejected')

# Cấu hình nhập ảnh trực tiếp trong nhà
class HouseImageInline(admin.TabularInline):
    model = HouseImage
    extra = 1

# Cấu hình quản lý nhà
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'price', 'district', 'status', 'created_at')
    search_fields = ('name', 'address', 'owner__username', 'owner_phone')
    list_filter = ('status', 'district', 'house_type')
    inlines = [HouseImageInline]
    actions = [make_available, make_rejected]
    filter_horizontal = ('furniture',)

# Cấu hình Khách thuê
class TenantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'cccd', 'gender', 'created_by')
    search_fields = ('full_name', 'phone', 'cccd')
    list_filter = ('gender',)

# Cấu hình hợp đồng
class ContractAdmin(admin.ModelAdmin):
    list_display = ('renter', 'house', 'start_date', 'end_date', 'total_value', 'status')
    search_fields = ('renter__full_name', 'renter__phone', 'house__name')
    list_filter = ('status',)
    filter_horizontal = ('roommates',)

# Cấu hình Hồ sơ cá nhân
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')

admin.site.register(House, HouseAdmin)
admin.site.register(Furniture)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Tenant, TenantAdmin)
admin.site.register(Profile, ProfileAdmin)
