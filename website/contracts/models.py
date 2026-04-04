from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from houses.models import House

# Bảng Khách thuê (Tenant/Customer)
class Tenant(models.Model):
    GENDER_CHOICES = [
        ('male', 'Nam'),
        ('female', 'Nữ'),
    ]

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Quản lý bởi Chủ nhà")
    
    full_name = models.CharField(max_length=100, verbose_name="Họ tên khách thuê")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    cccd = models.CharField(max_length=20, verbose_name="CCCD")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Giới tính")
    dob = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    address = models.TextField(null=True, blank=True, verbose_name="Nơi thường trú")
    
    id_front_image = models.ImageField(upload_to='tenants/id_cards/', null=True, blank=True, verbose_name="Ảnh CCCD mặt trước")
    id_back_image = models.ImageField(upload_to='tenants/id_cards/', null=True, blank=True, verbose_name="Ảnh CCCD mặt sau")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    def __str__(self):
        return f"{self.full_name} ({self.phone})"


# Bảng Hợp đồng Thuê Nhà
class Contract(models.Model):

    STATUS_CHOICES = [
        ('active', 'Đang hiệu lực'),
        ('expired', 'Đã hết hạn'),
        ('terminated', 'Đã chấm dứt sớm'),
    ]

    house = models.ForeignKey(House, on_delete=models.SET_NULL, related_name='contracts', verbose_name="Nhà/Căn hộ cho thuê", null = True, blank = True)
    
    renter = models.ForeignKey(Tenant, on_delete=models.RESTRICT, related_name='signed_contracts', verbose_name="Người đại diện ký hợp đồng", null=True, blank=True)
    roommates = models.ManyToManyField(Tenant, blank=True, related_name='shared_contracts', verbose_name="Thành viên ở ghép")

    
    start_date = models.DateField(verbose_name="Ngày bắt đầu hiệu lực")
    end_date = models.DateField(verbose_name="Ngày kết thúc hợp đồng")
    
    total_value = models.BigIntegerField(verbose_name="Tổng giá trị hợp đồng (VNĐ)", null=True, blank=True, validators=[MinValueValidator(0)])
    contract_document = models.FileField(upload_to='contracts/', null=True, blank=True, verbose_name="Bản scan Hợp đồng/CCCD (PDF/ZIP)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Trạng thái hợp đồng")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    def __str__(self):
        house_name = self.house.name if self.house else "Nhà đã bị xoá"
        tenant_name = self.renter.full_name if self.renter else "Chưa có tên"
        return f"Hợp đồng thuê {house_name} - Đại diện: {tenant_name}"
