# LT-GIS_Motel-Room-Listing-Management
Lập trình GIS, ứng dụng GIS trong quản lý đăng tin phòng trọ tại tp.hcm

# Sau khi clone code về thực hiện các lệnh sau
1. Cập nhật username/password database của bản thân ở file ./website/website/settings.py
2. Cài đặt môi trường Django: pip install django
3. Tiến hành các thay đổi: python manage.py makemigrations
4. Áp dụng thay đổi: python manage.py migrate

# Lưu ý: Mở PostgreSQL trước khi run code để đảm bảo code chạy
Lệnh run: python manage.py runserver
Tạo user để test trang admin: python manage.py createsuperuser
