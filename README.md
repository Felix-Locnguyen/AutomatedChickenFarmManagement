# AutomatedChickenFarmManagement

## Project Overview

Một hệ thống quản lý trang trại gà thông minh sử dụng tự động hóa và giám sát dựa trên dữ liệu để tối ưu hóa hiệu quả chăn nuôi và sức khỏe gà.

## Project Status

**Current Stage:** Backend Development - Database Models Hoàn tất

Dự án hiện đang trong giai đoạn phát triển backend. Frontend đã hoàn tất với đầy đủ chức năng quản lý.

## Cập nhật gần đây (May 2026)

### Backend Development (May 1, 2026)

#### 1. Tối ưu Dashboard API với SQLAlchemy Query Functions

Tối ưu hiệu suất truy vấn trong `backend/api/routes/dashboard.py`:

**Import thêm:**
```python
from sqlalchemy import func
```

**`GET /api/dashboard/stats`:**
- `Coop.query.count()` thay `len(coops)`
- `db.session.query(func.sum(Coop.current_count)).scalar()` thay `sum(c.current_count for c in coops)`
- `db.session.query(func.sum(Coop.capacity)).scalar()` thay `sum(c.capacity for c in coops)`
- `Device.query.filter(Device.status == 'online').count()` thay list comprehension
- `Alert.query.filter(Alert.is_resolved == False).count()` thay list comprehension
- `Coop.query.filter(Coop.status == 'active').count()` cho từng trạng thái

**`GET /api/dashboard/alerts`:**
- Thêm filter `Alert.level.in_(['critical', 'warning'])` để chỉ lấy cảnh báo Critical/Warning
- Sắp xếp theo thời gian giảm dần, giới hạn 10 bản ghi

**Kết quả:** Tối ưu hiệu suất bằng cách tính toán ở cấp độ database thay vì Python

### Cập nhật gần đây (April 2026)

### Backend Development (April 29, 2026)

#### 1. Cấu trúc Backend

```
backend/
├── config.py              # Cấu hình ứng dụng (Development/Production/Testing)
├── requirements.txt       # Python dependencies
├── app.py                 # Flask application entry point (sắp tạo)
├── models.py              # Database Models (Flask-SQLAlchemy)
├── doc/
│   └── note.txt          # Tài liệu học tập về Flask
└── api/
    ├── __init__.py       # API Blueprint Factory
    └── routes/
        ├── __init__.py    # Export blueprints
        ├── auth.py        # Authentication: login, register, logout, me
        ├── coops.py       # Coop CRUD: create, read, update, delete, devices, environment, history
        ├── devices.py    # Device CRUD: connect, toggle, assign, update name
        ├── dashboard.py   # Dashboard: stats, alerts, recent activities
        └── camera.py      # Camera: list, detail, snapshot, stream, recordings
```

#### 2. Database Models (models.py)

Tạo file `backend/models.py` với 7 models sử dụng Flask-SQLAlchemy:

| # | Model | Mô tả | Relationships |
|---|-------|-------|---------------|
| 1 | User | Người dùng hệ thống | 1-N với Alert |
| 2 | Coop | Chuồng gà | 1-N với Environment, FeedSchedule, Alert; N-N với Device |
| 3 | Device | Thiết bị IoT | 1-N với Alert; N-N với Coop |
| 4 | CoopDevice | Bảng trung gian N-N | - |
| 5 | Environment | Dữ liệu môi trường | N-1 với Coop |
| 6 | FeedSchedule | Lịch cho ăn | N-1 với Coop |
| 7 | Alert | Cảnh báo | N-1 với Coop, Device |

**Tính năng:**
- `datetime.utcnow` cho các trường thời gian (created_at, updated_at, recorded_at)
- Mã hóa mật khẩu với `werkzeug.security.generate_password_hash` / `check_password_hash`
- Method `to_dict()` cho mỗi model (trả về JSON cho API)
- Validation với `unique`, `nullable`, `default` constraints

**Database Schema:**

```
users:
    id (PK), username (unique), email (unique), password_hash, full_name, role, created_at, updated_at

coops:
    id (PK), name, location, capacity, current_count, area,
    temp_min, temp_max, humidity_min, humidity_max, feed_threshold, water_threshold,
    feed_time_1, feed_time_2, feed_time_3,
    auto_fan, auto_light, auto_feed, auto_water,
    emergency_alert, status, created_at, updated_at

devices:
    id (PK), name, type, mac_address (unique), status, is_active, battery, created_at, updated_at

coop_devices:
    id (PK), coop_id (FK), device_id (FK), is_active, created_at

environments:
    id (PK), coop_id (FK), temperature, humidity, feed_level, water_level, recorded_at

feed_schedules:
    id (PK), coop_id (FK), time, amount, enabled, created_at

alerts:
    id (PK), coop_id (FK), device_id (FK), type, level, message, is_resolved, created_at, resolved_at
```

**Cách sử dụng trong app.py:**
```python
from flask import Flask
from config import config
from models import db

app = Flask(__name__)
app.config.from_object(config['development'])
db.init_app(app)

with app.app_context():
    db.create_all()
```

#### 2. API Endpoints Đã Tạo

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/auth/login` | Đăng nhập, trả về JWT token |
| POST | `/api/auth/register` | Đăng ký tài khoản mới |
| GET | `/api/auth/me` | Lấy thông tin user hiện tại |
| POST | `/api/auth/logout` | Đăng xuất |
| GET | `/api/coops` | Danh sách tất cả chuồng |
| POST | `/api/coops` | Tạo chuồng mới |
| GET | `/api/coops/<id>` | Lấy thông tin một chuồng |
| PUT | `/api/coops/<id>` | Cập nhật thông tin chuồng |
| DELETE | `/api/coops/<id>` | Xóa chuồng |
| GET | `/api/coops/<id>/devices` | Lấy thiết bị trong chuồng |
| GET | `/api/coops/<id>/environment` | Lấy dữ liệu môi trường mới nhất |
| GET | `/api/coops/<id>/history` | Lấy lịch sử dữ liệu môi trường |
| GET | `/api/devices` | Danh sách tất cả thiết bị |
| POST | `/api/devices` | Tạo thiết bị mới |
| POST | `/api/devices/connect` | Kết nối thiết bị mới (QR/Mã) |
| GET | `/api/devices/<id>` | Lấy thông tin thiết bị |
| PUT | `/api/devices/<id>` | Cập nhật thiết bị |
| DELETE | `/api/devices/<id>` | Xóa thiết bị |
| POST | `/api/devices/<id>/toggle` | Bật/tắt thiết bị |
| POST | `/api/devices/<id>/assign` | Gán thiết bị vào chuồng |
| PATCH | `/api/devices/<id>/name` | Cập nhật tên thiết bị |
| GET | `/api/dashboard` | Tổng quan dashboard |
| GET | `/api/dashboard/stats` | Thống kê chi tiết |
| GET | `/api/dashboard/alerts` | Danh sách cảnh báo |
| GET | `/api/dashboard/recent-activities` | Hoạt động gần đây |
| GET | `/api/camera` | Danh sách camera |
| GET | `/api/camera/<id>` | Chi tiết camera |
| GET | `/api/camera/coop/<coop_id>` | Camera theo chuồng |
| POST | `/api/camera/<id>/snapshot` | Chụp ảnh snapshot |
| GET | `/api/camera/<id>/stream` | Lấy URL stream |
| GET | `/api/camera/<id>/recordings` | Danh sách recordings |

#### 3. Chức Năng Thêm Thiết Bị (device-list.html)

Tích hợp flow thêm thiết bị IoT vào trang `device-list.html`:

- **Màn hình chọn phương thức**: Quét QR / Nhập mã
- **Quét QR**: Sử dụng thư viện jsQR cho tương thích tốt nhất
- **Nhập mã**: Input validation + connect API
- **Trạng thái chờ**: Loading spinner animation
- **Thành công**: Input tên thiết bị + xác nhận
- **Thất bại**: Hiển thị nguyên nhân + retry/back

**State Machine**:
```
select → scan/input → waiting → success/fail
```

**CSS Mobile-first** với responsive design.

### 1. Trang Camera và Camera Detail (April 28, 2026)

#### 1.1 Tạo trang camera-detail.html

- **Khu vực hiển thị camera:**
  - Chỉ hiển thị Live badge + Timestamp + Nút Phóng to toàn màn hình
  - Không có chức năng chụp ảnh/quay video (tối ưu hệ thống)
  - Giao diện tối giản, tập trung vào nội dung camera

- **Bảng thông tin tổng quát (lấy từ Coop Detail):**
  - Số lượng gà
  - Diện tích chuồng
  - Vị trí chuồng
  - Trạng thái hoạt động (badge)
  - Nhiệt độ + Độ ẩm
  - **Thức ăn + Nước** (mới bổ sung)
  - Danh sách thiết bị và trạng thái hoạt động

- **Dữ liệu động theo từng chuồng:**
  - Load từ query parameter `?coop=A/B/C/D/E`
  - Mỗi chuồng có thông tin riêng (số lượng gà, diện tích, vị trí, thiết bị)
  - Redirect về camera.html nếu không có param hợp lệ

#### 1.2 Cập nhật camera.html

- Đổi button "Kiểm tra" thành link với href tương ứng:
  - Chuồng A → `camera-detail.html?coop=A`
  - Chuồng B → `camera-detail.html?coop=B`
  - ... (tương tự cho C, D, E)

- **Sửa lỗi layout card:**
  - Đổi layout thành CSS Grid: 1 cột (mobile) → 2 cột (tablet) → 3 cột (desktop)
  - Thêm `min-height: 160px` cho card đồng nhất kích thước
  - Footer buttons sử dụng `margin-top: auto` để luôn ở dưới cùng

#### 1.3 Fixed Bottom Navigation

- FAB Navigation hiển thị cố định ở cạnh dưới màn hình trên mobile
- 5 mục: Chuồng, Thiết bị, Trang chủ, Camera, Khác
- Z-index cao, không bị che bởi nội dung khác

### 2. Biểu đồ tròn (Donut Chart) cho trạng thái thiết bị

- **coop-list.html**: Thay thế Pie Chart (Chart.js) bằng Donut Chart SVG
  - Dữ liệu mẫu: 15 thiết bị (9 hoạt động, 3 chờ, 3 lỗi)
  - Tương tác: hover segment hiển thị tooltip
  - Legend bên dưới với màu sắc tương ứng

- **coop-detail.html**: Di chuyển Donut Chart xuống dưới Area Chart
  - Thêm card "Thiết bị trong chuồng" với Donut Chart
  - Thêm danh sách thiết bị chi tiết bên cạnh

- **device-detail.html**: Cập nhật Donut Chart với thiết kế mới
  - Giữ nguyên vị trí (col-12, full width)
  - Sử dụng class `.donut-chart-container-detail`
  - Tương tác hover với tooltip

- **index.html**: Thay thế Pie Chart bằng Donut Chart SVG (giống coop-list)

### 2. Giá trị trung bình các chuồng

- **coop-list.html** và **index.html**: Thay thế Area Chart bằng card hiển thị giá trị
  - Tiêu đề: "Giá trị trung bình các chuồng"
  - 2 giá trị: Nhiệt độ (27°C), Độ ẩm (65%)
  - Giao diện đồng bộ với coop-detail

### 3. Fixed Bottom Navigation

- **Thêm vào 7 trang**: index.html, coop-list.html, coop-detail.html, device-list.html, device-detail.html, camera.html, other.html
- **5 mục** sắp xếp từ trái sang phải:
  1. Chuồng → coop-list.html
  2. Thiết bị → device-list.html
  3. Trang chủ → index.html
  4. Camera → camera.html
  5. Khác → other.html

- **Tính năng**:
  - Fixed position ở cạnh dưới màn hình
  - Hiển thị trên mobile (max-width: 767px)
  - Ẩn sidebar trên mobile
  - Icon Font Awesome + text

### 4. Trang mới

- **camera.html**: Trang theo dõi camera (đang phát triển)
- **other.html**: Trang chức năng mở rộng (đang phát triển)

### 5. Danh sách chuồng dạng Card

- Chuyển đổi từ bảng (table) sang card trong 4 trang:
  - **index.html**
  - **device-detail.html**
  - **device-list.html**
  - **coop-detail.html**

- **Mỗi card hiển thị**:
  - Tên chuồng (Chuồng A, B, C, D, E)
  - Số lượng gà (ví dụ: 480 gà)
  - Số lượng thiết bị (ví dụ: 4 thiết bị)
  - Trạng thái với màu sắc:
    - 🎯 Xanh lá (#22c55e): Bình thường
    - ⚠️ Vàng (#ffc107): Cảnh báo
    - 🔴 Đỏ (#dc3545): Lỗi

- **CSS**:
  ```css
  .coop-summary-card {
      display: flex;
      flex-direction: column;
      min-height: 70px;
      width: 100%;
      max-width: 100%;
  }
  ```

### 6. Sửa lỗi 404 Page

- **sb-admin-2.css**: Cập nhật class `.error`
  - Giảm font-size từ 7rem xuống 3rem
  - Đổi màu chữ thành đỏ (#dc3545)
  - Căn giữa với text-align: center và margin: 0 auto
  - Giảm width từ 12.5rem xuống 4rem

### 7. Thiết bị gần đây dạng Card

- Chuyển đổi từ bảng (table) sang card trong 4 trang:
  - **index.html**
  - **device-list.html**
  - **device-detail.html**
  - **coop-list.html**

- **Mỗi card hiển thị**:
  - Tên thiết bị (ví dụ: Cảm biến nhiệt A1)
  - Tên chuồng chứa thiết bị (ví dụ: Chuồng A)
  - Trạng thái với dấu chấm và nhãn:
    - 🟢 Xanh (#22c55e): Hoạt động
    - 🟡 Vàng (#ffc107): Đang chờ
    - 🔴 Đỏ (#dc3545): Ngắt kết nối

- **CSS**:
  ```css
  .device-recent-card {
      display: flex;
      flex-direction: column;
      border-left: 4px solid #22c55e;
      border-radius: 8px;
      padding: 10px 12px;
      min-height: 60px;
  }
  .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
  }
  ```

### Các trang đã cập nhật

| Trang | Thay đổi |
|-------|----------|
| `index.html` | Donut chart, Giá trị TB, Card chuồng, Card thiết bị, Bottom Nav |
| `coop-list.html` | Donut chart, Giá trị TB, Card thiết bị, Bottom Nav |
| `coop-detail.html` | Donut chart, Card chuồng, Bottom Nav |
| `device-list.html` | Card chuồng, Card thiết bị, Bottom Nav |
| `device-detail.html` | Donut chart, Card chuồng, Card thiết bị, Bottom Nav |
| `camera.html` | Card layout, Link đến camera-detail, Bottom Nav |
| `camera-detail.html` | **Trang mới** - Camera view + Thông tin tổng quát (Số lượng gà, Diện tích, Vị trí, Trạng thái, Nhiệt độ, Độ ẩm, Thức ăn, Nước, Thiết bị), Bottom Nav |
| `other.html` | Trang mới, Bottom Nav |
| `sb-admin-2.css` | Sửa lỗi 404 error page |

## Tech Stack

| Component | Technology | Version |
|----------|-----------|--------|
| Frontend Framework | Bootstrap | 4.6.0 |
| JavaScript Library | jQuery | 3.6.0 |
| Charts | Chart.js | 3.x |
| Tables | DataTables | 1.11 |
| Icons | Font Awesome | 6.0 |
| Backend | Python | 3.x |
| Database | SQLite (planned) | - |

## Project Structure

```
AutomatedChickenFarmManagement/
├── README.md              # This file
├── .gitignore
├── coop_page_structure.txt # Coop page structure notes
├── static/                # Frontend static files (SB Admin 2 theme)
│   ├── README.md          # Static files documentation
│   ├── index.html       # Dashboard - Trang chính
│   ├── coop-list.html   # Coop List - Danh sách chuồng
│   ├── coop-detail.html # Coop Detail - Chi tiết chuồng
│   ├── device-list.html # Device List - Danh sách thiết bị
│   ├── device-detail.html # Device Detail - Chi tiết thiết bị
│   ├── camera.html      # Camera - Theo dõi camera
│   ├── camera-detail.html # Camera Detail - Chi tiết camera từng chuồng
│   ├── other.html       # Other - Chức năng khác
│   ├── forms.html      # Forms - Tổng hợp tất cả form Bootstrap
│   ├── buttons.html   # Buttons components
│   ├── cards.html    # Cards components
│   ├── tables.html   # DataTables examples
│   ├── charts.html   # Chart.js examples
│   ├── login.html   # Login page
│   ├── register.html # Registration page
│   ├── forgot-password.html
│   ├── blank.html   # Blank page
│   ├── 404.html    # Error page
│   ├── utilities-*.html  # Bootstrap utilities
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   ├── vendor/          # Third-party libraries
│   ├── img/             # Images
│   └── scss/            # SCSS source files
├── backend/               # Flask Backend API
│   ├── README.md          # Backend documentation
│   ├── config.py         # Configuration (Dev/Prod/Test)
│   ├── requirements.txt  # Python dependencies
│   ├── app.py            # Flask entry point (TẠO MỚI)
│   ├── models.py         # Database models ✓
│   ├── api/
│   │   ├── __init__.py   # Blueprint factory
│   │   └── routes/
│   │       ├── auth.py      # Login, Register, Logout
│   │       ├── coops.py     # Coop CRUD
│   │       ├── devices.py   # Device management
│   │       ├── dashboard.py # Statistics
│   │       └── camera.py    # Camera control
│   └── doc/
│       └── note.txt      # Flask concepts
└── templates/           # (Planned) Django/Flask templates
```

## Progress Today (April 26, 2026)

### Changes Made to `coop-detail.html`

#### 1. Removed "Save" button in header
- Removed the "Lưu" button from the page header

#### 2. Redesigned Edit Modal
- Created a modal-based "Edit Settings" interface with blur background effect
- Removed the in-page edit form section

#### 3. Editable Fields in Modal
- Coop name, Location, Capacity, Current chickens, Area
- Temperature min/max, Humidity min/max
- Feed threshold, Water threshold
- Feeding schedule (Time 1, 2, 3)
- Automation toggles: Auto fan, Auto light, Auto feed, Auto water
- Removed "Status" field from editing

#### 4. Emergency Alert Field
- Added "Cho phép thông báo khẩn cấp" field with prominent styling (red border, warning label)

#### 5. Modal Actions
- Rollback button: Restores original values
- Save button: Shows confirmation dialog
- Confirmation dialog: "Bạn có muốn lưu thông tin này không?" with "Hủy" and "Lưu" options
- Success notification: Full-screen "Đã cập nhật thông tin thành công"

#### 6. Redesigned Area Chart
- Removed "Options" dropdown
- Changed title to "Biểu đồ" with data type dropdown on the left
- Single-select dropdown with options: Temperature, Humidity, Feed, Water, Chicken count
- Default state: Empty with "Chọn dữ liệu để xem biểu đồ" message
- No default chart displayed
- X-axis: T2, T3, T4, T5, T6, T7, CN (7 days)
- Y-axis: Auto-adjusts based on selected data type (°C, %, kg, liters, con)
- Capacity line (dashed) when "Chicken count" is selected
- Tooltip on hover: Shows time and value

#### 7. Fixed Chart Display Issue
- Fixed chart positioning to use single container
- Used absolute positioning to prevent overlap
- Removed conflicting Chart.js auto-loading

#### 8. Removed Pie Chart
- Removed "Trạng thái thiết bị" pie chart from the page

## Progress Today (April 27, 2026)

### Changes Made to `device-detail.html`

#### 1. Page Title and Header Changes
- Changed page title from "Thiết bị IoT" to "Quản lý thiết bị chuồng trại"
- Updated sidebar: "Thiết bị IoT" → "Quản lý thiết bị"
- Removed "Cập nhật thông tin thiết bị" form section
- Removed "Thêm thiết bị" button from page header

#### 2. Add Device Modal (Thêm thiết bị vào chuồng)
- Added "+ Thêm thiết bị" button in "Danh sách thiết bị trong Chuồng" card header
- Modal with blur background effect, centered on screen
- Search input with placeholder "Tìm thiết bị..."
- Checkbox list with 5 sample devices
- Real-time counter: "Đã chọn: X thiết bị"
- Two buttons: "Hủy" and "Thêm thiết bị"
- Success notification: Full-screen green background
- Warning toast: "Vui lòng chọn thiết bị" (yellow)
- Error toast: "Không thành công, vui lòng thử lại" (red)
- Toast positioned center-top with 25px offset, min-width 350px

#### 3. Redesigned Device List (Card Layout)
- Each device displayed as individual card
- Status dot indicators: ● Green (Hoạt động), ● Yellow (Chờ), ● Red (Lỗi)
- Device info: Name, Battery %, Connection status
- Toggle button: "Bật" (green) / "Tắt" (gray)
- Delete button with "Xóa" text
- Removed Settings (gear) button
- Removed table-based layout
- Device card layout:
  ```
  | ● Device Name |
  | 🔋 85%  📶 Đã kết nối |
  | [Bật]  [Xóa] |
  ```

#### 4. Mobile Responsive Design
- CSS optimized with green color #22c55e
- Page title: 20px, font-weight 600, line-height 1.3
- Card header: flexbox with justify-content: space-between
- Device cards: border-left 4px solid #22c55e, border-radius 8px
- Responsive: max-width 576px - cards stack vertically
- Toggle switch: 50px x 26px for better touch target

#### 5. Scrollable Device List
- Container with max-height: 400px (desktop), 300px (mobile)
- overflow-y: auto with smooth scrolling
- Custom scrollbar styling (6px width, gray thumb)
- Prevents page from becoming too long with >10 devices

#### 6. Donut Chart (Trạng thái thiết bị)
- Removed Area Chart (Nhiệt độ trung bình các chuồng)
- New Donut Chart design:
  - Center circle with total device count (5)
  - 3 segments: Hoạt động 60% (green), Chờ 20% (yellow), Lỗi 20% (red)
  - Legend below: "Hoạt động (3)", "Chờ (1)", "Lỗi (1)"
- Hover interactions:
  - Segment highlight with brightness increase
  - Tooltip at cursor position showing: Name + Percentage
  - Legend text changes color to match hovered segment
- Click outside to reset

#### 7. Toggle Logic Based on Connection Status
- Added `data-connection-status` attribute to device cards:
  - `connected`: Allows toggle, shows "Đã bật/Đã tắt" toast
  - `connecting`: Click shows warning "Thiết bị đang kết nối, vui lòng thử lại sau"
  - `disconnected`: Click shows error "Thiết bị không kết nối với chuồng, vui lòng kiểm tra lại kết nối"

#### 8. Sample Device Data

| # | Device Name | Status | Connection | Pin/Signal | Toggle |
|---|-------------|--------|-------------|------------|--------|
| 1 | Cảm biến nhiệt độ A1 | Hoạt động | connected | 85%, Đã kết nối | Bật |
| 2 | Cảm biến ẩm A1 | Hoạt động | connected | 92%, Đã kết nối | Bật |
| 3 | Quạt thông gió A1 | Hoạt động | connected | Quạt công nghiệp | Bật |
| 4 | Đèn LED A1 | Chờ | connecting | 70%, Chờ kết nối | Tắt |
| 5 | Hệ thống cho ăn B1 | Lỗi | disconnected | Mất kết nối | Tắt |

### Sample Code Structure

#### Device Card HTML
```html
<div class="device-card status-active" 
     data-device-id="1" 
     data-device-name="Cảm biến nhiệt độ A1" 
     data-connection-status="connected">
    <div class="device-card-row device-card-header">
        <span class="status-dot active"></span>
        <span class="device-name">Cảm biến nhiệt độ A1</span>
    </div>
    <div class="device-card-row device-card-info">
        <span><i class="fas fa-battery-full"></i> 85%</span>
        <span><i class="fas fa-wifi"></i> Đã kết nối</span>
    </div>
    <div class="device-card-row device-card-actions">
        <button class="btn btn-sm status-btn status-on device-toggle-btn">Bật</button>
        <button class="btn btn-sm btn-outline-danger btn-delete-device">Xóa</button>
    </div>
</div>
```

#### Donut Chart SVG
```html
<svg viewBox="0 0 200 200">
    <circle class="donut-segment" data-segment="hoatdong" 
            data-name="Hoạt động" data-percent="60" ... />
    <circle class="donut-segment" data-segment="cho" 
            data-name="Chờ" data-percent="20" ... />
    <circle class="donut-segment" data-segment="loi" 
            data-name="Lỗi" data-percent="20" ... />
    <circle cx="100" cy="100" r="50" fill="white" />
</svg>
```

### Key CSS Classes

| Class | Purpose |
|-------|---------|
| `.device-card` | Individual device card container |
| `.device-list-container` | Scrollable container with max-height |
| `.status-btn` | Toggle button (Bật/Tắt) |
| `.donut-chart` | SVG donut chart container |
| `.donut-segment` | Individual chart segment |
| `.donut-tooltip` | Tooltip displayed on hover |
| `.legend-item` | Legend items below chart |

## Features Planned

### 1. Dashboard & Monitoring
- [x] Tổng quan trang trại
- [x] Số lượng gà hiện tại
- [x] Tình trạng sức khỏe
- [x] Nhiệt độ, độ ẩm chuồng
- [x] Biểu đồ thống kê
- [x] Trạng thái thiết bị (Donut Chart)

### 2. Quản lý đàn gà
- [x] Quản lý chuồng (basic UI)
- [ ] Thêm/xóa/sửa thông tin gà
- [ ] Theo dõi tuổi, giống, cân nặng
- [ ] Ghi chép tiêm phòng
- [ ] Lịch sử sức khỏe

### 3. Quản lý cho ăn
- [x] Lịch cho ăn tự động
- [ ] Cài đặt lượng thức ăn
- [ ] Thống kê tiêu thụ

### 4. Quản lý chuồng
- [x] Giám sát môi trường (nhiệt độ, độ ẩm)
- [x] Điều khiển quạt, đèn tự động
- [x] Cảnh báo nhiệt độ
- [x] Thiết bị IoT

### 6. Giao diện Mobile
- [x] Fixed Bottom Navigation với 5 mục
- [x] Ẩn sidebar trên mobile
- [x] Responsive design cho card chuồng

### 5. Báo cáo
- [ ] Xuất báo cáo Excel/PDF
- [ ] Biểu đồ tăng trọng
- [ ] Thống kê sản lượng trứng

## Forms Reference (forms.html)

Trang `forms.html` chứa tất cả các loại form Bootstrap 4:

### Form Controls
- Text Input (email, password, number, tel, url, search)
- Textarea
- Select (default, multiple)
- File Upload
- Date/Time inputs
- Color picker, Range slider

### Checkboxes & Radios
- Default (stacked, inline)
- Custom Checkbox
- Custom Radio
- Custom Select
- Custom File Input

### Layout
- Form Groups
- Form Grid (columns)
- Horizontal Form
- Inline Forms
- Input Group (prepend/append)

### Validation
- Help Text
- Disabled Forms
- Custom Styles (JS)
- Server Side (.is-valid/.is-invalid)
- Tooltips

## Key Pages

| Page | Purpose |
|-----|---------|
| `static/index.html` | Main dashboard entry point |
| `static/coop-list.html` | Coop list management |
| `static/coop-detail.html` | Coop detail with chart |
| `static/device-list.html` | IoT device list |
| `static/device-detail.html` | Device detail with toggle |
| `static/camera.html` | Camera monitoring - Danh sách camera |
| `static/camera-detail.html` | Camera detail - Xem camera từng chuồng |
| `static/other.html` | Other functions |
| `static/forms.html` | Form components reference |

## API Endpoints (Đã triển khai)

```
# Auth
POST   /api/auth/login      # Đăng nhập, nhận JWT token
POST   /api/auth/register   # Đăng ký user mới
GET    /api/auth/me         # Lấy thông tin user hiện tại
POST   /api/auth/logout     # Đăng xuất

# Coops
GET    /api/coops                # Danh sách chuồng
POST   /api/coops                # Tạo chuồng mới
GET    /api/coops/<id>           # Chi tiết chuồng
PUT    /api/coops/<id>           # Cập nhật chuồng
DELETE /api/coops/<id>           # Xóa chuồng
GET    /api/coops/<id>/devices  # Thiết bị trong chuồng
GET    /api/coops/<id>/environment  # Dữ liệu môi trường
GET    /api/coops/<id>/history  # Lịch sử dữ liệu

# Devices
GET    /api/devices              # Danh sách thiết bị
POST   /api/devices              # Tạo thiết bị mới
POST   /api/devices/connect      # Kết nối thiết bị (QR/mã)
GET    /api/devices/<id>         # Chi tiết thiết bị
PUT    /api/devices/<id>         # Cập nhật thiết bị
DELETE /api/devices/<id>         # Xóa thiết bị
POST   /api/devices/<id>/toggle # Bật/tắt thiết bị
POST   /api/devices/<id>/assign # Gán thiết bị vào chuồng
PATCH  /api/devices/<id>/name   # Đặt tên thiết bị

# Dashboard
GET    /api/dashboard               # Tổng quan
GET    /api/dashboard/stats         # Thống kê chi tiết
GET    /api/dashboard/alerts        # Danh sách cảnh báo
GET    /api/dashboard/recent-activities  # Hoạt động gần đây

# Camera
GET    /api/camera                  # Danh sách camera
GET    /api/camera/<id>             # Chi tiết camera
GET    /api/camera/coop/<id>        # Camera theo chuồng
POST   /api/camera/<id>/snapshot   # Chụp ảnh
GET    /api/camera/<id>/stream     # Lấy URL stream
GET    /api/camera/<id>/recordings # Danh sách recordings
```

## Database Schema (Đã thiết kế)

### User
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| username | VARCHAR | Tên đăng nhập (unique) |
| email | VARCHAR | Email (unique) |
| password_hash | VARCHAR | Password đã hash |
| full_name | VARCHAR | Họ tên |
| role | VARCHAR | Vai trò (admin/user) |
| created_at | DATETIME | Ngày tạo |
| updated_at | DATETIME | Ngày cập nhật |

### Coop
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| name | VARCHAR | Tên chuồng |
| location | VARCHAR | Vị trí |
| capacity | INTEGER | Sức chứa tối đa |
| current_count | INTEGER | Số lượng gà hiện tại |
| area | FLOAT | Diện tích (m²) |
| temp_min | FLOAT | Nhiệt độ tối thiểu |
| temp_max | FLOAT | Nhiệt độ tối đa |
| humidity_min | FLOAT | Độ ẩm tối thiểu |
| humidity_max | FLOAT | Độ ẩm tối đa |
| feed_threshold | FLOAT | Ngưỡng thức ăn |
| water_threshold | FLOAT | Ngưỡng nước |
| feed_time_1 | TIME | Giờ cho ăn lần 1 |
| feed_time_2 | TIME | Giờ cho ăn lần 2 |
| feed_time_3 | TIME | Giờ cho ăn lần 3 |
| auto_fan | BOOLEAN | Tự động bật quạt |
| auto_light | BOOLEAN | Tự động bật đèn |
| auto_feed | BOOLEAN | Tự động cho ăn |
| auto_water | BOOLEAN | Tự động cấp nước |
| emergency_alert | BOOLEAN | Thông báo khẩn cấp |
| status | VARCHAR | Trạng thái (normal/warning/error) |

### Device
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| name | VARCHAR | Tên thiết bị |
| type | VARCHAR | Loại (sensor/fan/light/feeder/camera) |
| mac_address | VARCHAR | Địa chỉ MAC |
| status | VARCHAR | Trạng thái (online/offline/connecting) |
| is_active | BOOLEAN | Bật/tắt |
| battery | INTEGER | % pin |
| created_at | DATETIME | Ngày tạo |

### CoopDevice (Many-to-Many)
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| coop_id | INTEGER | FK to Coop |
| device_id | INTEGER | FK to Device |
| is_active | BOOLEAN | Kích hoạt |

### Environment
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| coop_id | INTEGER | FK to Coop |
| temperature | FLOAT | Nhiệt độ (°C) |
| humidity | FLOAT | Độ ẩm (%) |
| feed_level | FLOAT | Mức thức ăn (%) |
| water_level | FLOAT | Mức nước (%) |
| recorded_at | DATETIME | Thời gian ghi nhận |

### FeedSchedule
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| coop_id | INTEGER | FK to Coop |
| time | TIME | Giờ cho ăn |
| amount | FLOAT | Lượng thức ăn |
| enabled | BOOLEAN | Bật/tắt |

### Alert
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| coop_id | INTEGER | FK to Coop |
| device_id | INTEGER | FK to Device |
| type | VARCHAR | Loại cảnh báo |
| level | VARCHAR | Mức độ (info/warning/error) |
| message | TEXT | Nội dung |
| is_resolved | BOOLEAN | Đã xử lý |
| created_at | DATETIME | Thời gian tạo |

## Setup Instructions

### Frontend Only
```bash
# Mở trong trình duyệt
static/index.html
# Hoặc chạy local server
python -m http.server 8000 --directory static
```

### Full Setup (Backend + Frontend)
```bash
# 1. Di chuyển vào thư mục backend
cd backend

# 2. Tạo virtual environment
python -m venv venv

# 3. Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Cài đặt dependencies
pip install -r requirements.txt

# 5. Chạy server
python app.py
# Hoặc
flask run

# 6. Truy cập
# Frontend: http://localhost:5000
# API: http://localhost:5000/api/
```

### API Test
```bash
# Đăng nhập
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Lấy dashboard (cần token)
curl -X GET http://localhost:5000/api/dashboard \
  -H "Authorization: Bearer <token>"
```

## Backend Documentation

Xem chi tiết tại: `backend/README.md`

## Notes for Development
| amount | FLOAT | Lượng thức ăn |
| enabled | BOOLEAN | Bật/tắt |

### Environment
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| coop_id | INTEGER | Mã chuồng |
| temperature | FLOAT | Nhiệt độ |
| humidity | FLOAT | Độ ẩm |
| feed_level | FLOAT | Mức thức ăn |
| water_level | FLOAT | Mức nước |
| recorded_at | DATETIME | Thời gian |

## Setup Instructions

### Frontend Only (Current)
```bash
# Open in browser
static/index.html
```

### Full Setup (Planned)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows

# Install dependencies
pip install flask flask-sqlalchemy

# Run server
flask run
```

## Notes for Development

1. **Frontend First**: Dự án được phát triển theo hướng Frontend trước, sau đó mới tích hợp Backend
2. **Static Files**: Tất cả frontend sử dụng SB Admin 2 theme
3. **API Design**: Backend RESTful API với JWT authentication
4. **Database**: Sử dụng SQLite cho development, có thể scale lên PostgreSQL
5. **Device Connection**: Frontend hỗ trợ kết nối thiết bị qua QR Code hoặc nhập mã thủ công

## License

MIT License