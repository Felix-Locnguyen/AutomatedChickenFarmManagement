# Backend Plan - Automated Chicken Farm Management

## 1. Project Overview

**Mục tiêu:** Xây dựng Backend RESTful API để hỗ trợ Frontend quản lý trang trại gà

**Tech Stack:**
- Framework: Flask (Python 3.x)
- Database: SQLite (development) / PostgreSQL (production)
- ORM: SQLAlchemy
- Authentication: JWT

## 2. Project Structure

```
AutomatedChickenFarmManagement/
├── app.py                    # Flask app chính
├── requirements.txt          # Dependencies
├── config.py                 # Cấu hình
├── instance/                  # SQLite database
├── models.py                 # SQLAlchemy Models
├── static/                    # Frontend (đã có)
├── templates/                 # HTML templates (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── coop-list.html
│   ├── coop-detail.html
│   ├── device-list.html
│   ├── device-detail.html
│   ├── camera.html
│   ├── camera-detail.html
│   ├── other.html
│   └── login.html
└── api/
    ├── __init__.py
    ├── routes/
    │   ├── __init__.py
    │   ├── auth.py        # Authentication routes
    │   ├── coops.py       # Coop CRUD
    │   ├── devices.py    # Device CRUD
    │   ├── dashboard.py  # Dashboard data
    │   └── camera.py     # Camera data
    └── utils/
        ├── __init__.py
        └── helpers.py
```

## 3. Database Models

### 3.1 User Model

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='admin')  # admin, staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3.2 Coop Model

```python
class Coop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # A, B, C, D, E
    location = db.Column(db.String(200))
    capacity = db.Column(db.Integer, default=500)
    current_count = db.Column(db.Integer, default=0)
    area = db.Column(db.Float, default=50.0)  # m²
    
    # Environment thresholds
    temp_min = db.Column(db.Float, default=20.0)
    temp_max = db.Column(db.Float, default=30.0)
    humidity_min = db.Column(db.Float, default=40.0)
    humidity_max = db.Column(db.Float, default=70.0)
    feed_threshold = db.Column(db.Float, default=20.0)
    water_threshold = db.Column(db.Float, default=30.0)
    
    # Feed schedule
    feed_time_1 = db.Column(db.Time, default=datetime.time(6, 0))
    feed_time_2 = db.Column(db.Time, default=datetime.time(12, 0))
    feed_time_3 = db.Column(db.Time, default=datetime.time(18, 0))
    
    # Automation settings
    auto_fan = db.Column(db.Boolean, default=True)
    auto_light = db.Column(db.Boolean, default=True)
    auto_feed = db.Column(db.Boolean, default=True)
    auto_water = db.Column(db.Boolean, default=True)
    
    # Alerts
    emergency_alert = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')  # active, warning, error
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3.3 Device Model

```python
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # temperature, humidity, fan, light, feed, camera
    mac_address = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='offline')  # online, offline, connecting
    is_active = db.Column(db.Boolean, default=True)
    battery = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3.4 CoopDevice (Many-to-Many)

```python
class CoopDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coop_id = db.Column(db.Integer, db.ForeignKey('coop.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    is_active = db.Column(db.Boolean, default=True)
```

### 3.5 Environment Data

```python
class Environment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coop_id = db.Column(db.Integer, db.ForeignKey('coop.id'))
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    feed_level = db.Column(db.Float)  # Percentage
    water_level = db.Column(db.Float)  # Percentage
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 3.6 Feed Schedule

```python
class FeedSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coop_id = db.Column(db.Integer, db.ForeignKey('coop.id'))
    time = db.Column(db.Time, nullable=False)
    amount = db.Column(db.Float, default=10.0)  # kg
    enabled = db.Column(db.Boolean, default=True)
```

### 3.7 Alert/Log

```python
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coop_id = db.Column(db.Integer, db.ForeignKey('coop.id'))
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    type = db.Column(db.String(50))  # temperature, humidity, feed, water, device
    level = db.Column(db.String(20))  # info, warning, error
    message = db.Column(db.Text)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## 4. API Endpoints

### 4.1 Authentication

| Method | Endpoint | Mô tả |
|--------|---------|--------|
| POST | `/api/auth/login` | Đăng nhập |
| POST | `/api/auth/register` | Đăng ký |
| POST | `/api/auth/logout` | Đăng xuất |
| GET | `/api/auth/me` | Thông tin user hiện tại |

### 4.2 Dashboard

| Method | Endpoint | Mô tả |
|--------|---------|--------|
| GET | `/api/dashboard` | Tổng quan trang trại |
| GET | `/api/dashboard/stats` | Thống kê nhanh |
| GET | `/api/dashboard/alerts` | Cảnh báo gần đây |

### 4.3 Coops

| Method | Endpoint | Mô tả |
|--------|---------|--------|
| GET | `/api/coops` | Danh sách chuồng |
| POST | `/api/coops` | Tạo chuồng mới |
| GET | `/api/coops/<id>` | Chi tiết chuồng |
| PUT | `/api/coops/<id>` | Cập nhật chuồng |
| DELETE | `/api/coops/<id>` | Xóa chuồng |
| GET | `/api/coops/<id>/devices` | Thiết bị trong chuồng |
| GET | `/api/coops/<id>/environment` | Dữ liệu môi trường |
| GET | `/api/coops/<id>/history` | Lịch sử dữ liệu |

### 4.4 Devices

| Method | Endpoint | Mô tả |
|--------|---------|--------|
| GET | `/api/devices` | Danh sách thiết bị |
| POST | `/api/devices` | Thêm thiết bị mới |
| GET | `/api/devices/<id>` | Chi tiết thiết bị |
| PUT | `/api/devices/<id>` | Cập nhật thiết bị |
| DELETE | `/api/devices/<id>` | Xóa thiết bị |
| POST | `/api/devices/<id>/toggle` | Bật/Tắt thiết bị |
| POST | `/api/devices/<id>/assign` | Gán thiết bị vào chuồng |

### 4.5 Feed Schedule

| Method | Endpoint | Mô tả |
|--------|---------|--------|
| GET | `/api/feed-schedule` | Danh sách lịch cho ăn |
| POST | `/api/feed-schedule` | Tạo lịch mới |
| PUT | `/api/feed-schedule/<id>` | Cập nhật lịch |
| DELETE | `/api/feed-schedule/<id>` | Xóa lịch |

### 4.6 Environment

| Method | Endpoint | Mô tả |
|--------|---------|--------|
| POST | `/api/environment` | Ghi dữ liệu môi trường |
| GET | `/api/environment/<coop_id>` | Lấy dữ liệu hiện tại |
| GET | `/api/environment/<coop_id>/history` | Lịch sử dữ liệu |

### 4.7 Alerts

| Method | Endpoint | Mô tả |
|--------|---------|--------|
| GET | `/api/alerts` | Danh sách cảnh báo |
| PUT | `/api/alerts/<id>/resolve` | Đánh dấu đã xử lý |

## 5. Pages (Jinja2 Routes)

| Endpoint | Page | Mô tả |
|----------|------|--------|
| GET | `/` | Dashboard |
| GET | `/coops` | Danh sách chuồng |
| GET | `/coops/<id>` | Chi tiết chuồng |
| GET | `/devices` | Danh sách thiết bị |
| GET | `/devices/<id>` | Chi tiết thiết bị |
| GET | `/cameras` | Danh sách camera |
| GET | `/cameras/<coop>` | Camera chi tiết |
| GET | `/other` | Tiện ích |
| GET | `/login` | Đăng nhập |

## 6. Data Flow

```
[Frontend]
    │
    ├──► API Calls (fetch/axios)
    │         │
    ▼         ▼
[Flask Routes] ──► [SQLAlchemy Models]
    │              │
    │              ▼
    │        [SQLite/PostgreSQL]
    │
    ▼
[Response JSON]
    │
    ▼
[Frontend Update DOM]
```

## 7. Frontend Integration

### 7.1 API Service (JavaScript)

```javascript
// api.js
const API_BASE = '/api';

const api = {
    // Dashboard
    getDashboard: () => fetch(`${API_BASE}/dashboard`).then(r => r.json()),
    
    // Coops
    getCoops: () => fetch(`${API_BASE}/coops`).then(r => r.json()),
    getCoop: (id) => fetch(`${API_BASE}/coops/${id}`).then(r => r.json()),
    updateCoop: (id, data) => fetch(`${API_BASE}/coops/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(r => r.json()),
    
    // Devices
    getDevices: () => fetch(`${API_BASE}/ devices`).then(r => r.json()),
    toggleDevice: (id) => fetch(`${API_BASE}/devices/${id}/toggle`, {
        method: 'POST'
    }).then(r => r.json()),
    
    // Auth
    login: (credentials) => fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(credentials)
    }).then(r => r.json()),
};
```

### 7.2 Data Loading Pattern

```javascript
// Load coop list on page load
async function loadCoops() {
    const response = await fetch('/api/coops');
    const coops = await response.json();
    
    coops.forEach(coop => {
        const card = createCoopCard(coop);
        document.getElementById('coop-list').appendChild(card);
    });
}
```

## 8. Sample Data (Seeding)

### 8.1 Default Coops

| Name | Capacity | Current | Area | Temp Range | Humidity Range |
|------|----------|---------|------|-----------|--------------|
| A | 500 | 480 | 50 | 20-30 | 40-70 |
| B | 500 | 450 | 50 | 20-30 | 40-70 |
| C | 500 | 420 | 50 | 20-30 | 40-70 |
| D | 500 | 500 | 50 | 20-30 | 40-70 |
| E | 500 | 380 | 50 | 20-30 | 40-70 |

### 8.2 Default Devices

| Name | Type | Coop | Status |
|------|------|------|--------|
| Cảm biến nhiệt A1 | temperature | A | online |
| Cảm biến ẩm A1 | humidity | A | online |
| Quạt thông gió A1 | fan | A | online |
| Đèn LED A1 | light | A | online |
| Cảm biến nhiệt B1 | temperature | B | online |
| Cảm biến ẩm B1 | humidity | B | online |
| Quạt thông gió B1 | fan | B | online |
| Đèn LED B1 | light | B | online |
| Camera A | camera | A | online |
| Camera B | camera | B | online |

### 8.3 Initial Environment Data

Random values in ranges:
- Temperature: 22-28°C
- Humidity: 55-75%
- Feed Level: 30-90%
- Water Level: 40-95%

## 9. Implementation Order

| Priority | Task | Mô tả |
|----------|------|-------|
| 1 | Setup Flask + SQLAlchemy | Cơ bản |
| 2 | Models | Tạo database models |
| 3 | Seed Data | Dữ liệu mẫu |
| 4 | Basic API | CRUD cơ bản |
| 5 | Dashboard API | API tổng quan |
| 6 | Auth | Đăng nhập/đăng ký |
| 7 | Frontend Integration | Gọi API từ frontend |
| 9 | Real-time Updates | WebSocket (optional) |
| 10 | Production Deploy | Deploy thật |

## 10. Dependencies

```
flask==3.0.0
flask-sqlalchemy==3.1.1
flask-jwt-extended==4.6.0
flask-cors==4.0.0
python-dotenv==1.0.0
werkzeug==3.0.1
```

## 11. Configuration

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chicken_farm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
```

## 12. Progress Tracking

- [ ] Setup Flask project
- [ ] Create database models
- [ ] Seed initial data
- [ ] Implement Authentication
- [ ] Implement Dashboard API
- [ ] Implement Coop CRUD API
- [ ] Implement Device CRUD API
- [ ] Implement Feed Schedule API
- [ ] Implement Environment API
- [ ] Integration với frontend
- [ ] Testing
- [ ] Deployment