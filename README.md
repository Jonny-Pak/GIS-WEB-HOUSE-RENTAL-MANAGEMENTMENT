# LT-GIS: Hệ thống Quản lý Đăng tin Phòng trọ (WebGIS)

Dự án ứng dụng công nghệ WebGIS trong việc quản lý, tìm kiếm và đăng tin phòng trọ trên địa bàn TP.HCM.

---

## Cấu trúc thư mục

```text
GIS-WEB-HOUSE-RENTAL-MANAGEMENTMENT/
├── docker-compose.yml          # Cấu hình Docker Compose (web + PostgreSQL)
├── Dockerfile                  # Build image cho Django app
├── requirements.txt            # Danh sách thư viện Python
├── media/                      # Thư mục chứa file upload (ảnh nhà, CCCD, hợp đồng...)
├── README.md
│
└── website/                    # ── Django Project Root ──
    ├── manage.py               # Entry point (DJANGO_SETTINGS_MODULE = config.settings)
    │
    ├── config/                 # Cấu hình trung tâm của project
    │   ├── settings.py         #   Cài đặt Django (DB, apps, middleware...)
    │   ├── urls.py             #   Bảng định tuyến gốc — phân luồng URL tới từng app
    │   ├── wsgi.py             #   WSGI entry point (cho deploy production)
    │   └── asgi.py             #   ASGI entry point (cho deploy async)
    │
    ├── accounts/               # App: Tài khoản & Xác thực
    │   ├── models.py           #   Profile (1-1 với User)
    │   ├── views.py            #   Đăng ký, xem hồ sơ
    │   ├── urls.py             #   /auth/login, /auth/register, /auth/profile
    │   └── admin.py            #   Đăng ký ProfileAdmin
    │
    ├── houses/                 # App: Quản lý Nhà cho thuê (Core Domain)
    │   ├── models.py           #   House, Furniture, HouseImage
    │   ├── views.py            #   Trang chủ, chi tiết nhà, bản đồ, dashboard, đăng/sửa/xóa bài
    │   ├── urls.py             #   /, /map/, /house-detail/<id>/, /dashboard/...
    │   ├── forms.py            #   HouseForm (form đăng tin)
    │   ├── admin.py            #   HouseAdmin + custom filter/actions (duyệt, từ chối)
    │   ├── services/           #   Tầng Business Logic (tách khỏi views)
    │   │   ├── house_service.py    # Tìm kiếm bán kính (Haversine), tìm kiếm vùng vẽ (Shapely)
    │   │   └── geocoding.py        # Chuyển địa chỉ → tọa độ (Nominatim API)
    │   └── api/                #   REST API (DRF) cho bản đồ
    │       ├── views.py        #     API tìm nhà theo bán kính, theo polygon vẽ
    │       ├── serializers.py  #     HouseSerializer (chuyển đổi Model → JSON)
    │       └── urls.py         #     /api/v1/houses/, /api/v1/polygon-search/
    │
    ├── contracts/              # App: Quản lý Hợp đồng & Khách thuê
    │   ├── models.py           #   Tenant (khách thuê), Contract (hợp đồng)
    │   ├── views.py            #   Tạo hợp đồng, quản lý hợp đồng, quản lý khách thuê
    │   ├── urls.py             #   /contracts/manage-contracts/, /contracts/manage-tenants/
    │   ├── forms.py            #   TenantForm, ContractForm
    │   └── admin.py            #   TenantAdmin, ContractAdmin
    │
    ├── custom_admin/           # App: Trang Quản trị Tùy chỉnh (thay thế Django Admin)
    │   ├── views.py            #   Dashboard, CRUD User/House/Furniture, Read-only Tenant/Contract
    │   ├── urls.py             #   /custom-admin/...
    │   └── forms.py            #   AdminUserCreateForm, AdminHouseForm, AdminFurnitureForm
    │
    ├── templates/              # Templates tập trung (HTML — xử lý phía server)
    │   ├── layouts/            #   Base templates dùng chung (base.html, dashboard_base.html)
    │   ├── home.html           #   Trang chủ
    │   ├── accounts/           #   Templates cho accounts (login, register, profile)
    │   ├── houses/             #   Templates cho houses (chi tiết nhà, bản đồ)
    │   ├── dashboard/          #   Templates cho dashboard người dùng
    │   └── custom_admin/       #   Templates cho trang quản trị
    │
    └── static/                 # Tài nguyên tĩnh (CSS, JS, Fonts, Images — gửi thẳng xuống trình duyệt)
        ├── css/
        ├── fonts/
        └── images/
```

---

## Giải thích kiến trúc: Tại sao cấu trúc như thế này?

### 1. Tại sao tách ra nhiều App thay vì để một chỗ?

Django khuyến khích mỗi app chỉ đảm nhận **một nhóm nghiệp vụ** (Single Responsibility). Nếu để tất cả model, view, form vào một app duy nhất, khi project phát triển sẽ:

- File `views.py` phình lên hàng nghìn dòng, rất khó tìm code
- Nhiều người cùng sửa một file → xung đột Git liên tục
- Không thể hiểu nhanh phạm vi ảnh hưởng khi thay đổi code

Cách chia hiện tại:

| App | Nghiệp vụ | Lý do tách riêng |
|-----|-----------|-------------------|
| `accounts` | Đăng nhập, đăng ký, hồ sơ | Auth là tính năng độc lập, hầu như không thay đổi khi phát triển thêm |
| `houses` | Nhà cho thuê, bản đồ, API | Core domain — phần lớn logic nghiệp vụ nằm ở đây |
| `contracts` | Hợp đồng, khách thuê | Có model riêng (Tenant, Contract), flow nghiệp vụ riêng (tạo HĐ → đổi trạng thái nhà) |
| `custom_admin` | Trang quản trị | Admin có giao diện, quyền, flow hoàn toàn khác với user thường |

### 2. Tại sao `config/` thay vì dùng tên project mặc định?

Khi chạy `django-admin startproject`, Django tạo folder cùng tên project (ví dụ: `GIS_WEB_HOUSE_RENTAL_MANAGEMENTMENT/settings.py`). Tên quá dài, khó gõ mỗi lần import.

Đổi thành `config/` giúp:
- Ngắn gọn, dễ nhớ: `config.settings`, `config.urls`
- Convention phổ biến trong cộng đồng Django
- Thể hiện rõ mục đích: đây là folder **cấu hình**, không chứa logic nghiệp vụ

### 3. Tại sao `houses/services/` — Service Layer?

Thông thường Django để business logic trong views. Nhưng khi logic trở nên phức tạp (tính toán Haversine, geocoding, Shapely polygon...), để trong views sẽ:

- View dài, khó đọc, khó test
- Không tái sử dụng được (nếu cần dùng ở view khác hoặc management command)

**Service Layer** giải quyết vấn đề đó:

```text
View (nhận request, trả response)
  └── gọi Service (xử lý logic nghiệp vụ)
        └── gọi Model (truy vấn database)
```

Ví dụ cụ thể:
- `house_service.py` → Tính khoảng cách Haversine, tìm nhà trong polygon
- `geocoding.py` → Chuyển địa chỉ thành tọa độ (gọi Nominatim API)

Cả API views lẫn web views đều gọi chung services → **không viết lại logic**.

### 4. Tại sao API nằm trong `houses/api/` thay vì app riêng?

API bản chất là **một cách phục vụ dữ liệu** (trả JSON thay vì HTML). Nó không phải một domain nghiệp vụ riêng.

```text
houses/
├── views.py      → Phục vụ qua giao diện web (HTML)
├── api/views.py  → Phục vụ qua API (JSON)
└── services/     → Logic chung cho cả hai
```

Nếu tách `api` thành app riêng:
- API import model từ `houses`, import service từ `houses` → phụ thuộc hoàn toàn vào `houses`
- Nếu sau này `contracts` cũng cần API → lại tạo thêm app? Không hợp lý
- Giữ API trong app chủ → dễ tìm, dễ hiểu, đúng Single Responsibility

### 5. Tại sao Templates tập trung (`templates/`) thay vì mỗi app một folder?

Django hỗ trợ cả hai cách:
- **Cách 1**: `templates/` tập trung ← đang dùng
- **Cách 2**: `accounts/templates/accounts/`, `houses/templates/houses/`...

Chọn Cách 1 vì:
- Project quy mô nhỏ-vừa, ~20 templates → mở một folder là thấy hết
- Nhiều template dùng chung layout (`base.html`, `dashboard_base.html`) → quản lý tập trung tiện hơn
- Các app trong project này không cần tái sử dụng cho project khác

### 6. Tại sao `static/` và `templates/` ngang hàng, không lồng nhau?

Hai loại tài nguyên này phục vụ mục đích hoàn toàn khác:

| | `templates/` | `static/` |
|---|---|---|
| **Xử lý bởi** | Django template engine (server) | Trình duyệt tải trực tiếp (client) |
| **Nội dung** | HTML với biến, if/for, extends | CSS, JS, hình ảnh, fonts |
| **Khi deploy** | Django render ra HTML rồi gửi | Nginx/CDN phục vụ trực tiếp, không qua Django |

Để ngang hàng là **chuẩn Django convention**, tách rõ trách nhiệm server vs client.

### 7. Tại sao `media/` nằm ngoài `website/`?

`media/` chứa file do người dùng upload (ảnh nhà, CCCD, hợp đồng...). Đặt ngoài `website/` vì:
- **Không thuộc source code** — không nên commit vào Git
- **Khi deploy**, media thường lưu trên storage riêng (S3, CDN)
- Docker volume mount riêng, không ảnh hưởng khi rebuild container

### 8. Tại sao tách `custom_admin` thay vì gộp logic quản trị vào từng App con?

Một lựa chọn kiến trúc khác là phân bổ logic quản trị vào từng app riêng lẻ (ví dụ: `houses/admin_views.py`). Dù cách này đảm bảo tính đóng gói tốt (Domain-Driven Design), dự án vẫn quyết định gom tất cả giao diện quản trị vào một App trung tâm `custom_admin` vì 3 lý do cốt lõi:

- **Tính liên thông dữ liệu (Cross-Domain)**: Trang Dashboard thường cần vẽ biểu đồ và thống kê chéo nhiều bảng dữ liệu. Ví dụ: *Biểu đồ tỉ lệ Hợp đồng (`contracts`) thực tế theo từng khu vực Nhà trọ (`houses`)*. Đặt logic đa chiều này ở `custom_admin` đảm bảo tính trung lập, tránh việc một app phải gánh trách nhiệm của app khác.
- **Thống nhất Giao diện (Layout & Assets)**: Hệ thống quản trị nội bộ sử dụng một bộ khung Layout riêng rất phức tạp (Sidebar điều hướng chung, Chart.js, DataTables). Một app trung tâm giúp gom gọn toàn bộ cấu hình Template và CSS/JS thay vì bắt các app con chia nhau xử lý.
- **Màng lọc bảo mật (Security Choke Point)**: Mọi đường dẫn quản trị đều quy về một mạch máu duy nhất (ví dụ `/custom-admin/...`). Cấu trúc này giúp lập trình viên có thể đặt bức tường lửa chặn người dùng ngay từ URL tổng thông qua Route Grouping hoặc Middleware cực kỳ an toàn; triệt tiêu hoàn toàn rủi ro bị "lọt lưới" bảo mật do quên cấu hình phân quyền như khi code rải rác từng app.

---

## Luồng Xử lý Dữ liệu (Data Flow)

Dự án tuân thủ chặt chẽ mô hình **MVT (Model - View - Template)** của Django. Dưới đây là luồng Data đi từ lúc Client gửi yêu cầu đến lúc nhận được giao diện:

```text
[BƯỚC 1] 🌐 TRÌNH DUYỆT (Client) 
   └── Gửi Request: Gõ địa chỉ `http://.../house-detail/5/`

[BƯỚC 2] 🚦 config/urls.py (Bộ định tuyến gốc)
   └── Nhận Request, thấy khớp chữ "house-detail", bèn chuyển bưu phẩm gửi vào phòng ban (App) `houses/`

[BƯỚC 3] 🔀 houses/urls.py (Bộ định tuyến của App)
   └── Lọc ra được mã ID nhà là 5. Gọi ông "View" xử lý căn nhà số 5.

[BƯỚC 4] 🧠 houses/views.py (View - Nhạc trưởng điều phối)
   ├── 4.1. Có thể nhờ `services/house_service.py` xử lý các phép toán khó (như tính khoảng cách)
   └── 4.2. Ra lệnh cho `models.py` xuống kho (Database) bê món hàng số 5 lên.

[BƯỚC 5] 🗄️ houses/models.py (Model - Tương tác Database)
   └── Truy vấn CSDL, bê nguyên bộ dữ liệu tivi, tủ lạnh, giá thuê của Căn số 5 trả về cho View.

[BƯỚC 6] 🎨 templates/ (Template - Bộ mặt Layout)
   └── View cầm tệp dữ liệu đó, "đổ" (render) vào file `detail.html`. Trộn chung với `base.html` để có header, footer đẹp đẽ.

[BƯỚC 7] 🚀 TRẢ HÀNG (Response)
   └── View ném nguyên cục HTML siêu đẹp vừa trộn xong về lại cho Trình duyệt. Kết thúc nụ hôn!
```

---

## Yêu cầu

1. Docker Desktop
2. Git
3. (Tùy chọn) Python 3.11+ nếu chạy local không dùng Docker

## Chạy dự án bằng Docker

Tất cả lệnh bên dưới chạy tại thư mục gốc dự án (nơi có `docker-compose.yml`).

### 1. Clone source

```bash
git clone <repo-url>
cd GIS-WEB-HOUSE-RENTAL-MANAGEMENTMENT
```

### 2. Build và khởi động container

```bash
docker compose up --build -d
```

### 3. Migrate database

```bash
docker compose exec web python website/manage.py migrate
```

### 4. Tạo tài khoản admin

```bash
docker compose exec web python website/manage.py createsuperuser
```

### 5. Truy cập

| Trang | URL |
|-------|-----|
| Trang chủ | http://127.0.0.1:8000/ |
| Bản đồ | http://127.0.0.1:8000/map/ |
| Django Admin | http://127.0.0.1:8000/admin/ |
| Custom Admin | http://127.0.0.1:8000/custom-admin/ |
| API tìm nhà | http://127.0.0.1:8000/api/v1/houses/?lat=10.78&lng=106.70&radius=5 |

### 6. Lệnh hay dùng

```bash
# Xem trạng thái container
docker compose ps

# Xem log web
docker compose logs -f web

# Dừng hệ thống
docker compose down
```

## Lưu ý về dữ liệu khi làm nhóm

Dữ liệu PostgreSQL lưu trong Docker volume (`postgres_data`), không nằm trong Git. Thành viên mới clone code sẽ **không** tự động có data.

### Cách 1: Chia sẻ bản sao database

Tại máy đang có dữ liệu:

```bash
docker compose exec -T db pg_dump -U postgres -d quanlythuenha > backup.sql
```

Gửi `backup.sql` cho thành viên khác:

```bash
docker compose up -d db
docker compose exec -T db psql -U postgres -d quanlythuenha < backup.sql
```

### Cách 2: Dùng fixture (dữ liệu mẫu)

Xuất:

```bash
docker compose exec web python website/manage.py dumpdata --indent 2 > seed_data.json
```

Nhập tại máy mới:

```bash
docker compose up -d
docker compose exec web python website/manage.py migrate
docker compose exec web python website/manage.py loaddata seed_data.json
```

## Chạy local không dùng Docker

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python website/manage.py migrate
python website/manage.py runserver
```

> Lưu ý: Cần có PostgreSQL local và cấu hình biến môi trường kết nối DB.

## Quy trình làm việc nhóm với Git

Không code trực tiếp trên nhánh `dev`.

```bash
# Cập nhật dev
git checkout dev
git pull origin dev

# Tạo nhánh tính năng
git checkout -b feature/ten-tinh-nang

# Làm việc và đẩy code
git add .
git commit -m "feat: mô tả ngắn gọn"
git push -u origin feature/ten-tinh-nang
```

Tạo Pull Request để merge vào `dev` sau khi được review.
