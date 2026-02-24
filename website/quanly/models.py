from django.core.validators import MinValueValidator
from django.contrib.gis.db import models

from django.conf import settings

# Create your models here.

# Bảng Nội thất
class Furniture(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên nội thất")

    def __str__(self):
        return self.name

# Bảng Nhà
class House(models.Model):

    HOUSE_TYPE_CHOICES = [
        ('nguyencan', 'Nhà nguyên căn / Nhà phố'),
        ('chungcu', 'Căn hộ chung cư'),
        ('bietthu', 'Biệt thự'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('available', 'Đang cho thuê'),
        ('rented', 'Đã cho thuê'),
        ('hidden', 'Đã ẩn'),
        ('rejected', 'Bị từ chối'),
    ]

    DISTRICT_CHOICES = [
        ('q1', 'Quận 1'),
        ('q2', 'Quận 2'),
        ('q3', 'Quận 3'),
        ('q4', 'Quận 4'),
        ('q5', 'Quận 5'),
        ('q6', 'Quận 6'),
        ('q7', 'Quận 7'),
        ('q8', 'Quận 8'),
        ('q9', 'Quận 9'),
        ('q10', 'Quận 10'),
        ('q11', 'Quận 11'),
        ('q12', 'Quận 12'),
        ('qbt', 'Quận Bình Thạnh'),
        ('qtb', 'Quận Tân Bình'),
        ('qtp', 'Quận Tân Phú'),
        ('qp', 'Quận Phú Nhuận'),
        ('qgv', 'Quận Gò Vấp'),
        ('qbtan', 'Quận Bình Tân'),
        ('td', 'Thành phố Thủ Đức'),
        ('hbc', 'Huyện Bình Chánh'),
        ('hhm', 'Huyện Hóc Môn'),
        ('hcc', 'Huyện Củ Chi'),
        ('hnb', 'Huyện Nhà Bè'),
        ('hcg', 'Huyện Cần Giờ'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name="Chủ nhà", null=True, blank=True)
    owner_phone = models.CharField(max_length=15, verbose_name="Số điện thoại liên hệ")

    name = models.CharField(max_length=200, verbose_name="Tiêu đề bài đăng / Tên căn nhà")
    house_type = models.CharField(max_length=20, choices=HOUSE_TYPE_CHOICES, default='nguyencan', verbose_name="Loại Hình Nhà")
    price = models.BigIntegerField(verbose_name="Giá cho thuê (VNĐ/Tháng)", null=True, blank=True, validators=[MinValueValidator(0)])
    is_negotiable = models.BooleanField(default=False, verbose_name="Giá thỏa thuận")
    deposit = models.BigIntegerField(verbose_name="Tiền cọc (VNĐ)", null=True, blank=True, default=0, validators=[MinValueValidator(0)])
    electricity_price = models.CharField(max_length=100, verbose_name="Giá điện", default="Theo giá nhà nước", blank=True)
    water_price = models.CharField(max_length=100, verbose_name="Giá nước", default="Theo giá nhà nước", blank=True)
    area = models.FloatField(verbose_name="Diện tích sàn (m2)", default=0.0, validators=[MinValueValidator(0)])

    unit_count = models.IntegerField(verbose_name="Số lượng căn", default=1)
    room_count = models.IntegerField(verbose_name="Số lượng phòng", default=1)
    max_people = models.IntegerField(verbose_name="Số người ở tối đa", default=4)
    furniture = models.ManyToManyField(Furniture, verbose_name="Nội thất đi kèm", blank=True)

    district = models.CharField(max_length=10, choices=DISTRICT_CHOICES, verbose_name="Khu vực Quận/Huyện")
    address = models.TextField(verbose_name="Địa chỉ chi tiết (Số nhà, Ngõ/Hẻm, Đường)")
    
    # Bản đồ và vị trí (Đã chuyển sang PointField cho truy vấn GIS)
    location = models.PointField(srid=4326, geography=True,verbose_name="Tọa độ vị trí (Point)", null=True, blank=True)

    description = models.TextField(blank=True, verbose_name="Mô tả chi tiết")
    main_image = models.ImageField(upload_to='house/', null=True, blank=True, verbose_name="Ảnh đại diện")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái cho thuê")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    def __str__(self):
        return f"[{self.get_status_display()}] {self.name} - {self.get_district_display()}"


# Bảng Hình ảnh
class HouseImage(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='house_images/', verbose_name="Hình ảnh thêm")

    def __str__(self):
        return f"Ảnh của {self.house.name}"


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