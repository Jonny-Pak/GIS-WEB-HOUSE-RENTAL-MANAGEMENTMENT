from django.contrib import admin
from .models import House, Room, Furniture, HouseImage, Contract
# Register your models here.

# Duyệt bài đăng thuê nhà
@admin.action(description='Duyệt bài đăng')
def make_approved(modeladmin, request, queryset):
    queryset.update(status='approved')

# Cấu hình nhập phòng
class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ('room_number', 'area')

# Cấu hình nhập ảnh trực tiếp trong nhà
class HouseImageInline(admin.TabularInline):
    model = HouseImage
    extra = 1

# Cấu hình quản lý nhà
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'price', 'district', 'status', 'create_at') # Hiển thị cột
    search_fields = ('name', 'address', 'owner__username', 'owner_phone') # Thanh tìm kiếm
    list_filter = ('status', 'district', 'house_type') # Bộ lọc
    inlines = [HouseImageInline, RoomInline] # Nhúng form
    actions = [make_approved] # Nút chức năng

# Cấu hình quản lý phòng
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'house', 'area')
    search_fields = ('room_number', 'house__name')
    filter_horizontal = ('furnitures',)

# Cấu hình hợp đồng
class ContractAdmin(admin.ModelAdmin):
    list_display = ('tenant_name', 'house', 'start_date', 'end_date', 'total_value')
    search_fields = ('tenant_name', 'tenant_phone', 'house__name')

admin.site.register(House, HouseAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Furniture)
admin.site.register(Contract, ContractAdmin)