from django.contrib import admin
from .models import House, Furniture, HouseImage, Contract, Tenant
# Register your models here.

# Duyệt bài đăng thuê nhà
@admin.action(description='Duyệt bài đăng (Đang cho thuê)')
def make_available(modeladmin, request, queryset):
    queryset.update(status='available')

# Cấu hình nhập ảnh trực tiếp trong nhà
class HouseImageInline(admin.TabularInline):
    model = HouseImage
    extra = 1

# Cấu hình quản lý nhà (Sử dụng ModelAdmin thông thường)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'price', 'district', 'status', 'created_at') # Hiển thị cột
    search_fields = ('name', 'address', 'owner__username', 'owner_phone') # Thanh tìm kiếm
    list_filter = ('status', 'district', 'house_type') # Bộ lọc
    inlines = [HouseImageInline] # Nhúng form
    actions = [make_available] # Nút chức năng
    filter_horizontal = ('furniture',) # Chọn nội thất

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
    filter_horizontal = ('roommates',) # Chọn người ở ghép

admin.site.register(House, HouseAdmin)
admin.site.register(Furniture)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Tenant, TenantAdmin)
