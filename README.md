# 🏠 LT-GIS: Hệ thống Quản lý Đăng tin Phòng trọ (WebGIS)
Dự án ứng dụng công nghệ WebGIS trong việc quản lý, tìm kiếm và đăng tin phòng trọ trên địa bàn TP.HCM.

---

## 📂 Cấu trúc thư mục dự án

```text
GIS-WEB-HOUSE-RENTAL-MANAGEMENTMENT/
├── media/               # Nơi chứa các ảnh do người dùng upload (nhà trọ, hình ảnh phòng...)
├── website/             # Thư mục gốc chứa source code backend
│   ├── quanly/          # App chính (Chứa Models, Views, Templates, Static files)
│   ├── website/         # Thư mục cấu hình trung tâm (settings.py, urls.py)
│   └── manage.py        # File để thực thi các lệnh của Django
├── .gitignore           # File cấu hình chặn Git
├── requirements.txt     # Danh sách các thư viện cần cài đặt để chạy dự án
└── README.md            # Tài liệu hướng dẫn bạn đang đọc
```

---

## 🚀 Hướng dẫn cài đặt và chạy dự án (Dành cho nhà phát triển)


Vui lòng làm theo trình tự các bước dưới đây để đảm bảo dự án chạy ổn định trên máy của bạn.

### Bước 1: Clone dự án và thiết lập môi trường ảo
```bash
# Clone dự án về máy
git clone <đường-dẫn-repo-của-bạn>
cd GIS-WEB-HOUSE-RENTAL-MANAGEMENTMENT

# Tạo môi trường ảo (Tùy chọn nhưng RẤT KHUYẾN KHÍCH)
python -m venv .venv

# Kích hoạt môi trường ảo:
# - Trên Windows:
.venv\Scripts\activate
# - Trên MacOS/Linux:
source .venv/bin/activate
```

### Bước 2: Cài đặt thư viện
(Đảm bảo bạn đã kích hoạt môi trường ảo ở Bước 1)
```bash
# Cài đặt toàn bộ thư viện cần thiết (Django, psycopg2,...)
pip install -r requirements.txt
```

### Bước 3: Cấu hình Cơ sở dữ liệu (PostgreSQL)
1. Hãy chắc chắn rằng bạn đã cài đặt và bật phần mềm **PostgreSQL** trên máy tính phần mềm pgAdmin/DBeaver.
2. Mở file `website/website/settings.py`.
3. Tìm đến phần `DATABASES` và cập nhật lại thông số khớp với database Postgres của bạn:
   - `NAME`: Tên database bạn đã tạo.
   - `USER`: Tên đăng nhập postgresql (mặc định: postgres)
   - `PASSWORD`: Mật khẩu postgresql của bạn.

### Bước 4: Khởi tạo Database
```bash
# Di chuyển vào thư mục chứa file manage.py
cd website

# Tạo các bảng trong database
python manage.py makemigrations
python manage.py migrate
```

### Bước 5: Tạo tài khoản Admin (Quản trị viên)
```bash
python manage.py createsuperuser
```
*(Nhập username, email và password theo ý muốn)*

### Bước 6: Chạy Server
```bash
python manage.py runserver
```

### 🌐 Truy cập: 
- Trang web chính: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
- Trang quản trị Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🔄 Hướng dẫn cập nhật Code mới (Khi trong nhóm có người đẩy code lên)

Nếu máy của bạn đã clone dự án từ trước, bạn không cần phải làm lại từ Bước 1. Khi có người trong nhóm đẩy (push) code mới lên GitHub, bạn chỉ cần làm các bước sau để cập nhật máy của mình:

### Mở Terminal tại gốc dự án (nơi có file manage.py) và gõ:

```bash
# 1. Kéo code mới nhất từ nhánh dev trên GitHub về máy
git pull origin dev

# 2. Bật môi trường ảo (Nếu chưa bật)
.venv\Scripts\activate   # (Windows)

# 3. Cài đặt thêm thư viện mới (Phòng trường hợp bạn khác vừa cài thêm module mới vào requirements.txt)
pip install -r requirements.txt

# 4. Cập nhật Database (Phòng trường hợp bạn khác vừa thay đổi bảng Models)
python manage.py migrate

# 5. Chạy lại server bình thường
python manage.py runserver
```

---

## 🔀 Quy trình làm việc nhóm với Git (Branching Workflow)

Để tránh đụng độ code (conflict) và mất dữ liệu, **TUYỆT ĐỐI KHÔNG CODE TRỰC TIẾP TRÊN NHÁNH `dev`**. Vui lòng tuân thủ quy trình sau khi làm tính năng mới:

### Bước 1: Cập nhật nhánh gốc (dev)
```bash
git checkout dev
git pull origin dev
```

### Bước 2: Tạo nhánh riêng của bạn từ nhánh dev
```bash
# Đặt tên nhánh theo tính năng (VD: feature/login, feature/them-hoa-don...)
git checkout -b feature/ten-tinh-nang-cua-ban
```

### Bước 3: Code, Commit và Push lên nhánh riêng
```bash
# Sau khi bạn hoàn thành code trên nhánh của riêng mình
git add .
git commit -m "feat: mô tả ngắn gọn bạn vừa làm gì"

# Lần đầu tiên push nhánh mới lên GitHub, sử dụng lệnh này:
git push -u origin feature/ten-tinh-nang-cua-ban

# Các lần push sau trên cùng nhánh đó chỉ cần:
git push
```

### Bước 4: Tạo Pull Request (PR)
- Lên trang GitHub của dự án.
- Bấm vào nút **Compare & pull request** ở nhánh bạn vừa push.
- Xác nhận gộp nhánh `feature/ten-tinh-nang-cua-ban` vào nhánh `dev`.
- Nhờ Leader hoặc đồng đội Review Code và nhấn nút **Merge**.
