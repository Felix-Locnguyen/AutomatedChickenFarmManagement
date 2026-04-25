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
├── static/                # Frontend static files (SB Admin 2 theme)
│   ├── README.md          # Static files documentation
│   ├── index.html       # Dashboard - Trang chính
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

## Features Planned

### 1. Dashboard & Monitoring
- [ ] Tổng quan trang trại
- [ ] Số lượng gà hiện tại
- [ ] Tình trạng sức khỏe
- [ ] Nhiệt độ, độ ẩm chuồng
- [ ] Biểu đồ thống kê

### 2. Quản lý đàn gà
- [ ] Thêm/xóa/sửa thông tin gà
- [ ] Theo dõi tuổi, giống, cân nặng
- [ ] Ghi chép tiêm phòng
- [ ] Lịch sử sức khỏe

### 3. Quản lý cho ăn
- [ ] Lịch cho ăn tự động
- [ ] Cài đặt lượng thức ăn
- [ ] Thống kê tiêu thụ

### 4. Quản lý chuồng
- [ ] Giám sát môi trường (nhiệt độ, độ ẩm)
- [ ] Điều khiển quạt, đèn tự động
- [ ] Cảnh báo nhiệt độ

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

## API Endpoints (Planned)

```
GET    /api/dashboard          # Dashboard data
GET    /api/chickens         # List all chickens
POST   /api/chickens        # Add new chicken
GET    /api/chickens/<id>   # Get chicken details
PUT    /api/chickens/<id>   # Update chicken
DELETE /api/chickens/<id>   # Delete chicken
GET    /api/feed-schedule  # Feed schedule
POST   /api/feed-schedule # Add feed schedule
GET    /api/environment   # Environment data
POST   /api/environment  # Environment settings
GET    /api/reports      # Reports
```

## Database Schema (Planned)

### Chickens
| Field | Type | Description |
|-------|------|------------|
| id | INTEGER | Primary key |
| rfid_tag | VARCHAR | RFID tag number |
| breed | VARCHAR | Giống gà |
| birth_date | DATE | Ngày sinh |
| weight | FLOAT | Cân nặng hiện tại |
| gender | VARCHAR | Trống/Mái |
| status | VARCHAR | Trạng thái |
| created_at | DATETIME | Ngày tạo |

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

## Key Files for AI Agents

| File | Purpose |
|------|--------|
| `static/index.html` | Main dashboard entry point |
| `static/forms.html` | Form components reference |
| `static/README.md` | Detailed static files docs |

## Notes for Development

1. **Frontend First**: Dự án được phát triển theo hướng Frontend trước
2. **Static Files**: Tất cả frontend sử dụng SB Admin 2 theme
3. **API Design**: Backend sẽ được thiết kế RESTful API
4. **Database**: Sử dụng SQLite cho development, có thể scale lên PostgreSQL

## License

MIT License