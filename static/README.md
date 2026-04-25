# Static Files - SB Admin 2 Theme

## Giới thiệu

Thư mục `static/` chứa SB Admin 2 - một free Bootstrap 4 admin theme từ [Start Bootstrap](https://startbootstrap.com/theme/sb-admin-2).

## Cấu trúc thư mục

```
static/
├── index.html              # Trang Dashboard chính
├── forms.html           # Trang tổng hợp các loại form Bootstrap
├── buttons.html        # Các loại button
├── cards.html         # Cards component
├── tables.html       # DataTables examples
├── charts.html      # Chart.js examples
├── login.html       # Trang đăng nhập
├── register.html    # Trang đăng ký
├── forgot-password.html  # Trang quên mật khẩu
├── blank.html       # Trang trống
├── 404.html       # Trang lỗi 404
├── utilities-color.html      # Utilities - Colors
├── utilities-border.html    # Utilities - Borders
├── utilities-animation.html # Utilities - Animation
├── utilities-other.html     # Utilities - Other
├── css/
│   └── sb-admin-2.min.css  # Main CSS
├── js/
│   ├── sb-admin-2.min.js  # Main JS
│   └── demo/             # Demo scripts cho charts
├── vendor/           # Third-party libraries
│   ├── jquery/           # jQuery
│   ├── jquery-easing/     # jQuery Easing
│   ├── bootstrap/         # Bootstrap JS
│   ├── chart.js/         # Chart.js
│   ├── datatables/      # DataTables
│   └── fontawesome-free/ # Font Awesome
├── img/              # Images
└── scss/             # SCSS source files
```

## Các trang chính

### Dashboard (index.html)
Trang tổng quan với các thống kê:
- Earnings (Monthly/Annual)
- Earning (Environment)
- Pending Requests
- Pending Requests

### Forms (forms.html)
Trang tổng hợp **tất cả các loại form** trong Bootstrap 4:

**Form Controls:**
- Text Input (text, email, password, number, tel, url, search)
- Textarea (default, large)
- File Upload (single, multiple, accept types)
- Select (default, multiple)
- Date & Time (date, time, datetime-local, month, week, color, range)

**Checkboxes & Radios:**
- Default (stacked)
- Inline
- Disabled
- Custom Checkbox
- Custom Radio
- Custom Select
- Custom File Input

**Layout:**
- Form Groups
- Form Grid (columns)
- Form Row
- Horizontal Form
- Inline Forms
- Input Group (prepend, append, dropdown)

**Validation:**
- Help Text (block, inline)
- Disabled Forms (fieldset disabled)
- Validation Custom Styles (JavaScript validation)
- Validation Server Side (.is-valid, .is-invalid)
- Validation Tooltips

### Buttons (buttons.html)
Các loại button:
- Colors: primary, secondary, success, danger, warning, info, light, dark
- Sizes: large, default, small
- States: active, disabled
- Button Group
- Split Button Dropdowns

### Cards (cards.html)
Cards component examples:
- Basic Card
- Card with Header
- Card with Footer
- Image Cards
- Collapsible Card

## Cách sử dụng

### 1. Mở trực tiếp bằng trình duyệt
```bash
# Mở file index.html trong trình duyệt
static/index.html
```

### 2. Dùng với Python server
```bash
cd static
python -m http.server 8000
# Mở http://localhost:8000
```

### 3. Dùng với Node.js (http-server)
```bash
npx http-server static -p 8000
```

### 4. Copy vào Django static folder
```python
# settings.py
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

### 5. Copy vào Flask static folder
```python
app = Flask(__name__, static_folder='static')
```

## Các thư viện đi kèm

| Thư viện | Phiên bản | Mục đích |
|---------|---------|---------|
| jQuery | 3.6.0 | JavaScript framework |
| Bootstrap | 4.6.0 | CSS/JS framework |
| Chart.js | 3.x | Charts/Graphs |
| DataTables | 1.11 | Tables with pagination |
| Font Awesome | 6.0 | Icons |

## Tùy chỉnh

### Đổi màu sidebar
```css
/* Trong sb-admin-2.css */
.bg-gradient-primary {
    background-color: #4e73df; /* Đổi màu chính */
    background-image: linear-gradient(180deg, #4e73df 10%, #224abe 100%);
}
```

### Đổi màu chủ đạo
Tìm và thay thế mã màu `#4e73df` trong CSS.

## Tài liệu tham khảo

- [SB Admin 2 Original](https://startbootstrap.com/theme/sb-admin-2)
- [Bootstrap 4 Forms](https://getbootstrap.com/docs/4.0/components/forms/)
- [Bootstrap 4 Buttons](https://getbootstrap.com/docs/4.0/components/buttons/)
- [Bootstrap 4 Cards](https://getbootstrap.com/docs/4.0/components/card/)
- [Bootstrap 4 Utilities](https://getbootstrap.com/docs/4.0/utilities/borders/)

## License

SB Admin 2 được phát hành dưới [MIT License](LICENSE).

## Ghi chú

- Theme sử dụng Bootstrap 4 (không phải Bootstrap 5)
- Font Awesome 6 đã được tích hợp
- Charts sử dụng Chart.js
- Tables sử dụng DataTables với Bootstrap 4 theme