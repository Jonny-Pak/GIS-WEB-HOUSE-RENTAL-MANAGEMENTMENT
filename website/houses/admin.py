from django.contrib import admin
from django.contrib import messages
from .models import House, Furniture, HouseImage


# --- Filter tùy chỉnh ---
class RequiresCoordinatesFilter(admin.SimpleListFilter):
    title = 'Trạng thái tọa độ'
    parameter_name = 'coordinates'

    def lookups(self, request, model_admin):
        return [
            ('missing', 'Chờ nhập tọa độ'),
            ('complete', 'Đã có tọa độ'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'missing':
            return queryset.filter(requires_coordinates=True)
        if self.value() == 'complete':
            return queryset.filter(requires_coordinates=False)
        return queryset


# --- Actions cho House ---
@admin.action(description='Duyệt bài đăng (Đang cho thuê)')
def make_available(modeladmin, request, queryset):
    ready_queryset = queryset.filter(lat__isnull=False, lng__isnull=False)
    blocked_queryset = queryset.exclude(id__in=ready_queryset.values_list('id', flat=True))

    approved_count = ready_queryset.update(status='available', requires_coordinates=False)
    blocked_count = blocked_queryset.update(status='no_coordinates', requires_coordinates=True)

    if approved_count:
        modeladmin.message_user(
            request,
            f'Đã duyệt {approved_count} tin có đầy đủ tọa độ.',
            level=messages.SUCCESS,
        )
    if blocked_count:
        modeladmin.message_user(
            request,
            f'{blocked_count} tin chưa được duyệt vì chưa có tọa độ.',
            level=messages.WARNING,
        )


@admin.action(description='Từ chối bài đăng')
def make_rejected(modeladmin, request, queryset):
    queryset.update(status='rejected')


# Cấu hình nhập ảnh trực tiếp trong nhà
class HouseImageInline(admin.TabularInline):
    model = HouseImage
    extra = 1


# Cấu hình quản lý nhà
@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'price', 'status', 'requires_coordinates', 'created_at')
    search_fields = ('name', 'address', 'owner__username', 'owner_phone')
    list_filter = ('status', 'house_type', RequiresCoordinatesFilter)
    inlines = [HouseImageInline]
    actions = [make_available, make_rejected]
    filter_horizontal = ('furniture',)

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'owner', 'owner_phone', 'house_type', 'status')
        }),
        ('Địa chỉ & Tọa độ', {
            'fields': ('address', 'lat', 'lng', 'requires_coordinates'),
            'description': '<strong style="color: red;">Nhập lat/lng để xác định chính xác vị trí trên bản đồ</strong>'
        }),
        ('Thông tin chi tiết', {
            'fields': ('area', 'unit_count', 'room_count', 'max_people', 'furniture')
        }),
        ('Giá cả', {
            'fields': ('price', 'is_negotiable', 'deposit', 'electricity_price', 'water_price')
        }),
        ('Hình ảnh', {
            'fields': ('main_image',)
        }),
        ('Mô tả', {
            'fields': ('description',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        has_coordinates = obj.lat is not None and obj.lng is not None

        if obj.status == 'available' and not has_coordinates:
            obj.status = 'no_coordinates'
            obj.requires_coordinates = True
            self.message_user(
                request,
                'Không thể duyệt nhà khi chưa nhập đầy đủ kinh độ/vĩ độ.',
                level=messages.ERROR,
            )
            super().save_model(request, obj, form, change)
            return

        if has_coordinates:
            obj.requires_coordinates = False
        elif obj.status == 'available':
            obj.status = 'no_coordinates'
            obj.requires_coordinates = True

        super().save_model(request, obj, form, change)


@admin.register(Furniture)
class FurnitureAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
