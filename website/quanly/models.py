from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Bảng Nội thất
class Furniture(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên nội thất")
    description = models.TextField(blank=True, verbose_name="Mô tả tình trạng")

    def __str__(self):
        return self.name

# Bảng Nhà
class House(models.Model):

    HOUSE_TYPE_CHOICES = [
        ('nguyencan', 'Nhà nguyên căn'),
        ('chungcu', 'Căn hộ chung cư'),
        ('phong_tro', 'Phòng Trọ'),
    ]

    STATUS_CHOISE = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('hidden', 'Đã ẩn'),
        ('rejected', 'Bị từ chối'),
    ]

    DISTRICT_CHOPCES = [
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
        ('qtb', 'Quận Tân Bình'),
        ('qtp', 'Quận Tân Phú'),
        ('qbt', 'Quận Bình Thạnh'),
        ('td', 'Thủ Đức'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Chủ nhà", null=True, blank=True)
    owner_phone = models.CharField(max_length=10, verbose_name="Số điện thoại")

    name = models.CharField(max_length=200, verbose_name="Tên Căn Nhà")
    house_type = models.CharField(max_length=20, choices=HOUSE_TYPE_CHOICES, default='phong_tro', verbose_name="Loại nhà")
    price = models.IntegerField(verbose_name="Giá cho thuê (VNĐ)")
    deposit = models.IntegerField(verbose_name="Tiền cọc (VNĐ)")
    area = models.IntegerField(verbose_name="Diện tích nhà (m2)", default=20)

    district = models.CharField(max_length=10, choices= DISTRICT_CHOPCES, verbose_name= "Chọn Quận")
    address = models.TextField(verbose_name="Địa chỉ nhà")
    lat = models.FloatField(verbose_name="Vĩ độ", default=0.0)
    long = models.FloatField(verbose_name="Kinh độ", default=0.0)

    max_people = models.IntegerField(verbose_name="Số người ở tối đa", default=4)
    current_people = models.IntegerField(verbose_name="Số người đang ở", default=0)
    description = models.TextField(blank=True, verbose_name="Mô tả căn nhà")

    main_image = models.ImageField(upload_to= 'house/', null = True, blank= True, verbose_name= "Ảnh đại diện phòng")
    status = models.CharField(max_length=20, choices= STATUS_CHOISE, verbose_name= "Trạng thái")
    
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng")
    update_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    
    def __str__(self):
        return f"[{self.get_status_display()}] {self.name}"

# Bảng Phòng
class Room(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name="Thuộc căn nhà")
    room_number = models.CharField(max_length=50, verbose_name="Số phòng")
    area = models.IntegerField(verbose_name="Diện tích phòng (m2)", default=20)
    furnitures = models.ManyToManyField(Furniture, verbose_name="Nội thất đi kèm", blank=True)

    def __str__(self):
        return f"{self.room_number} - {self.house.name}"

# Bảng Hình ảnh
class HouseImage(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='house_images/', verbose_name="Hình ảnh")

    def __str__(self):
        return f"Ảnh của {self.house.name}"

# Bảng Hợp đồng Thuê Nhà
class Contract(models.Model):
    house = models.OneToOneField(House, on_delete=models.CASCADE, verbose_name="Hợp đồng thuê cho nhà")
    
    tenant_name = models.CharField(max_length=100, verbose_name="Họ tên khách thuê")
    tenant_phone = models.CharField(max_length=10, verbose_name="Số điện thoại")
    tenant_id = models.CharField(max_length=20, verbose_name="CCCD")
    start_date = models.DateField(verbose_name="Ngày bắt đầu thuê")
    end_date = models.DateField(verbose_name="Ngày kết thúc thuê")
    total_value = models.IntegerField(verbose_name="Tổng giá trị hợp đồng (VNĐ)", null=True, blank=True)

    def __str__(self):
        return f"Hợp đồng: {self.tenant_name} thuê {self.house.name}"