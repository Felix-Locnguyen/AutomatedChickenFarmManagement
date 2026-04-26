# AutomatedChickenFarmManagement

## Project Overview

Một hệ thống quản lý trang trại gà thông minh sử dụng tự động hóa và giám sát dựa trên dữ liệu để tối ưu hóa hiệu quả chăn nuôi và sức khỏe gà.

## Project Status

**Current Stage:** Đang phát triển - Frontend UI setup hoàn tất

Dự án hiện đang trong giai đoạn phát triển ban đầu. Frontend đã được thiết lập với SB Admin 2 theme.

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

## Features Planned

### 1. Dashboard & Monitoring
- [ ] Tổng quan trang trại
- [ ] Số lượng gà hiện tại
- [ ] Tình trạng sức khỏe
- [ ] Nhiệt độ, độ ẩm chuồng
- [x] Biểu đồ thống kê

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
| `static/device-detail.html` | Device detail |
| `static/forms.html` | Form components reference |

## API Endpoints (Planned)

```
GET    /api/dashboard          # Dashboard data
GET    /api/coops            # List all coops
POST   /api/coops           # Add new coop
GET    /api/coops/<id>      # Get coop details
PUT    /api/coops/<id>      # Update coop
DELETE /api/coops/<id>     # Delete coop
GET    /api/devices        # List all devices
POST   /api/devices       # Add new device
GET    /api/feed-schedule # Feed schedule
POST   /api/feed-schedule# Add feed schedule
GET    /api/environment   # Environment data
POST   /api/environment  # Environment settings
GET    /api/reports      # Reports
```

## Database Schema (Planned)

### Coops
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

### Devices
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| name | VARCHAR | Tên thiết bị |
| type | VARCHAR | Loại thiết bị |
| coop_id | INTEGER | FK to Coops |
| status | VARCHAR | Trạng thái |

### Health Records
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| chicken_id | INTEGER | FK to Chickens |
| record_date | DATE | Ngày ghi |
| weight | FLOAT | Cân nặng |
| notes | TEXT | Ghi chú |
| vaccine | VARCHAR | Vaccine đã tiêm |

### Feed Schedule
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| time | TIME | Giờ cho ăn |
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

1. **Frontend First**: Dự án được phát triển theo hướng Frontend trước
2. **Static Files**: Tất cả frontend sử dụng SB Admin 2 theme
3. **API Design**: Backend sẽ được thiết kế RESTful API
4. **Database**: Sử dụng SQLite cho development, có thể scale lên PostgreSQL

## License

MIT License