# Frontend Libraries Documentation

## Tổng quan

Dự án sử dụng các thư viện frontend đã có sẵn trong thư mục `static/vendor/`. Không cần tải thêm.

## Danh sách thư viện

### Core Libraries

| Thư viện | Phiên bản | Mục đích | Vị trí |
|----------|-----------|----------|--------|
| **jQuery** | 3.6.0 | JavaScript framework | `vendor/jquery/` |
| **Bootstrap** | 4.6.0 | CSS/JS Framework | `vendor/bootstrap/` |
| **Font Awesome** | 6.0 | Icons | `vendor/fontawesome-free/` |

### Charts & Data Visualization

| Thư viện | Phiên bản | Mục đích | Vị trí |
|----------|-----------|----------|--------|
| **Chart.js** | 3.x | Biểu đồ (Donut, Area, Pie) | `vendor/chart.js/` |

### Tables & Data

| Thư viện | Phiên bản | Mục đích | Vị trí |
|----------|-----------|----------|--------|
| **DataTables** | 1.11 | Tables với pagination | `vendor/datatables/` |

### Utilities

| Thư viện | Phiên bản | Mục đích | Vị trí |
|----------|-----------|----------|--------|
| **jQuery Easing** | - | Animation effects | `vendor/jquery-easing/` |

## Cách sử dụng trong HTML

```html
<!-- CSS -->
<link href="vendor/fontawesome-free/css/all.min.css" rel="stylesheet">
<link href="vendor/datatables/dataTables.bootstrap4.min.css" rel="stylesheet">
<link href="css/sb-admin-2.min.css" rel="stylesheet">

<!-- JavaScript -->
<script src="vendor/jquery/jquery.min.js"></script>
<script src="vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
<script src="vendor/jquery-easing/jquery.easing.min.js"></script>
<script src="vendor/chart.js/Chart.min.js"></script>

<!-- Custom JS -->
<script src="js/sb-admin-2.min.js"></script>
```

## API Integration

| File | Mục đích |
|------|----------|
| `static/js/api.js` | Wrapper cho Flask API (đã tạo mới) |

## Không cần cài đặt thêm

Tất cả thư viện đã được tải sẵn trong project. Không cần `npm install` hay bất kỳ package manager nào khác.