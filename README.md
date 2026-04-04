# LT-GIS: He thong Quan ly Dang tin Phong tro (WebGIS)

Du an ung dung cong nghe WebGIS trong viec quan ly, tim kiem va dang tin phong tro tren dia ban TP.HCM.

## Cau truc thu muc

```text
GIS-WEB-HOUSE-RENTAL-MANAGEMENTMENT/
|- docker-compose.yml
|- Dockerfile
|- requirements.txt
|- media/
|- website/
|  |- manage.py
|  |- accounts/       # Quản lý tài khoản (Auth)
|  |- api/            # API DRF (Bản đồ, Tìm kiếm)
|  |- contracts/      # Quản lý hợp đồng & khách thuê
|  |- houses/         # Quản lý thông tin nhà, geocoding
|  |- website/        # Root Config
|- README.md
```

## Yeu cau

1. Docker Desktop
2. Git
3. (Tuy chon) Python 3.11+ neu chay local khong dung Docker

## Chay du an bang Docker

Tat ca lenh ben duoi chay tai thu muc goc du an (noi co docker-compose.yml).

### 1. Clone source

```bash
git clone <repo-url>
cd GIS-WEB-HOUSE-RENTAL-MANAGEMENTMENT
```

### 2. Build va khoi dong container

```bash
docker compose up --build -d
```

### 3. Migrate database

```bash
docker compose exec web python website/manage.py migrate
```

### 4. Tao tai khoan admin

```bash
docker compose exec web python website/manage.py createsuperuser
```

### 5. Truy cap

1. Trang chu: http://127.0.0.1:8000/
2. Trang admin: http://127.0.0.1:8000/admin/

### 6. Lenh hay dung

```bash
# Xem trang thai container
docker compose ps

# Xem log web
docker compose logs -f web

# Dung he thong
docker compose down
```

## Luu y ve du lieu khi lam nhom

Du lieu PostgreSQL dang luu trong Docker volume (postgres_data), khong nam trong Git. Vi vay thanh vien moi clone code se KHONG tu dong co data tu may ban.

### Cach 1: Chia se ban sao database (giu nguyen du lieu that)

Thuc hien tren may cua nguoi dang co du lieu:

```bash
docker compose exec -T db pg_dump -U postgres -d quanlythuenha > backup.sql
```

Gui file backup.sql cho thanh vien khac. Sau do tren may thanh vien:

```bash
docker compose up -d db
docker compose exec -T db psql -U postgres -d quanlythuenha < backup.sql
```

### Cach 2: Dung du lieu mau (seed/fixture) trong repo

Xuat du lieu mau:

```bash
docker compose exec web python website/manage.py dumpdata --indent 2 > seed_data.json
```

Tai may clone moi:

```bash
docker compose up -d
docker compose exec web python website/manage.py migrate
docker compose exec web python website/manage.py loaddata seed_data.json
```

Khuyen nghi cho do an nhom:

1. Luu seed_data.json de ai clone ve cung co bo du lieu demo.
2. Dinh ky tao backup.sql theo moc de tranh mat du lieu.
3. Khong dua du lieu nhay cam that vao file backup/seed.

## Chay local khong dung Docker (tuy chon)

Neu muon chay khong Docker, ban tu quan ly PostgreSQL local va bien moi truong ket noi DB.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python website/manage.py migrate
python website/manage.py runserver
```

## Quy trinh lam viec nhom voi Git

Khong code truc tiep tren nhanh dev.

```bash
# Cap nhat dev
git checkout dev
git pull origin dev

# Tao nhanh tinh nang
git checkout -b feature/ten-tinh-nang

# Lam viec va day code
git add .
git commit -m "feat: mo ta ngan gon"
git push -u origin feature/ten-tinh-nang
```

Tao Pull Request de merge vao dev sau khi duoc review.
