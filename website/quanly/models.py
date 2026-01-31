from django.db import models

# Create your models here.

# Bảng Nội thất
class Furniture(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên nội thất")
    description = models.TextField(blank=True, verbose_name="Mô tả tình trạng")

    def __str__(self):
        return self.name

# Bảng Nhà
class House(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên Căn Nhà / Tòa nhà")
    address = models.TextField(verbose_name="Địa chỉ nhà")
    
    # Tọa độ (phục vụ bản đồ sau này)
    lat = models.FloatField(verbose_name="Vĩ độ", default=0.0)
    long = models.FloatField(verbose_name="Kinh độ", default=0.0)
    
    description = models.TextField(blank=True, verbose_name="Mô tả căn nhà")
    
    def __str__(self):
        return self.name

# Bảng Phòng
class Room(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name="Thuộc căn nhà")
    
    room_number = models.CharField(max_length=50, verbose_name="Số phòng")
    area = models.IntegerField(verbose_name="Diện tích (m2)", default=20)
    price = models.IntegerField(verbose_name="Giá cho thuê (VNĐ)")
    deposit = models.IntegerField(verbose_name="Tiền cọc (VNĐ)")
    max_people = models.IntegerField(verbose_name="Số người ở tối đa", default=4)
    current_people = models.IntegerField(verbose_name="Số người đang ở", default=0)
    furnitures = models.ManyToManyField(Furniture, verbose_name="Nội thất đi kèm", blank=True)
    is_rented = models.BooleanField(default=False, verbose_name="Trạng thái thuê?")

    def __str__(self):
        return f"{self.house.name} - {self.room_number}"

# Bảng Hình ảnh
class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/', verbose_name="Hình ảnh phòng")

    def __str__(self):
        return f"Ảnh của {self.room.room_number}"

# Bảng Hợp đồng Thuê Nhà
class Contract(models.Model):
    house = models.OneToOneField(House, on_delete=models.CASCADE, verbose_name="Hợp đồng thuê cho nhà")
    
    tenant_name = models.CharField(max_length=100, verbose_name="Họ tên khách thuê")
    tenant_phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    tenant_id = models.CharField(max_length=20, verbose_name="CCCD")
    start_date = models.DateField(verbose_name="Ngày bắt đầu thuê")
    end_date = models.DateField(verbose_name="Ngày kết thúc thuê")
    total_value = models.IntegerField(verbose_name="Tổng giá trị hợp đồng (VNĐ)", null=True, blank=True)

def __str__(self):
        return f"Hợp đồng: {self.tenant_name} thuê {self.house.name}"