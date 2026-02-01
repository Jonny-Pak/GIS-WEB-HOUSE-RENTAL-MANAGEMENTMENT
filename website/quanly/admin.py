from django.contrib import admin
from .models import House, Room, Furniture, RoomImage, Contract
# Register your models here.

# Duyệt bài đăng thuê nhà
@admin.action(description='Duyệt bài đăng')
def make_approved(modeladmin, request, queryset):
    queryset.update(is_approved=True)

# Cấu hình nhập phòng
class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ('room_number', 'area')

# Cấu hình quản lý nhà
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'price', 'address', 'is_approved', 'is_rented') # Hiển thị cột
    search_fields = ('name', 'address') # Thanh tìm kiếm
    list_filter = ('is_approved', 'owner', 'is_rented') # Bộ lọc
    inlines = [RoomInline] # Nhúng form
    actions = [make_approved] # Nút chức năng

# Cấu hình thêm ảnh nhà
class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

# Cấu hình quản lý phòng
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'house', 'area')
    search_fields = ('room_name', 'house__name')
    inlines = [RoomImageInline] 
    filter_horizontal = ('furnitures',)

# Cấu hình hợp đồng
class ContractAdmin(admin.ModelAdmin):
    list_display = ('tenant_name', 'house', 'start_date', 'end_date')

admin.site.register(House, HouseAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Furniture)
admin.site.register(Contract, ContractAdmin)