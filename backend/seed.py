"""
Script seed.py - Nạp dữ liệu mẫu vào cơ sở dữ liệu

Script này tạo dữ liệu mẫu cho hệ thống Quản lý Trang trại Gà.
Chạy độc lập với: python seed.py

Dữ liệu được tạo:
- 1 tài khoản admin
- 5 chuồng gà (A, B, C, D, E)
- 15 thiết bị IoT (3 thiết bị/ chuồng)
- 100 bản ghi dữ liệu môi trường (20/ chuồng)
- 15 lịch cho ăn (3/ chuồng)
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Thêm thư mục hiện tại vào path để import được config và models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import ứng dụng Flask và cấu hình
from flask import Flask
from config import config

# Import database models và db instance
from models import db, User, Coop, Device, CoopDevice, Environment, FeedSchedule, Alert


# =============================================================================
# KHỞI TẠO ỨNG DỤNG FLASK
# =============================================================================

def create_app():
    """Tạo và cấu hình Flask app cho script seed."""
    app = Flask(__name__)
    
    # Load cấu hình development (sử dụng SQLite cục bộ)
    app. config.from_object(config['development'])
    
    # Khởi tạo SQLAlchemy với app           
    db.init_app(app)
    
    return app


# =============================================================================
# SEED DỮ LIỆU NGƯỜI DÙNG
# =============================================================================

def seed_users():
    """
    Tạo tài khoản admin mặc định.
    
    Tài khoản admin được tạo:
    - Username: admin
    - Password: admin123 (đã được mã hóa bằng werkzeug)
    - Role: admin
    - Email: admin@chickenfarm.com
    """
    print("  Đang tạo tài khoản admin...")
    
    # Kiểm tra nếu admin đã tồn tại thì bỏ qua
    if User.query.filter_by(username='admin').first():
        print("    [Bỏ qua] Tài khoản admin đã tồn tại")
        return User.query.filter_by(username='admin').first()
    
    # Tạo user admin mới
    admin = User(
        username='admin',
        email='admin@chickenfarm.com',
        full_name='Quản trị viên',
        role='admin'
    )
    
    # Mã hóa mật khẩu bằng werkzeug.security.generate_password_hash
    # Đây là phương pháp bảo mật an toàn, sử dụng thuật toán pbkdf2:sha256
    admin.set_password('admin123')
    
    # Lưu vào database
    db.session.add(admin)
    db.session.commit()
    
    print(f"    [OK] Đã tạo tài khoản: {admin.username}")
    return admin


# =============================================================================
# SEED DỮ LIỆU CHUỒNG GÀ
# =============================================================================

def seed_coops():
    """
    Tạo 5 chuồng gà với thông tin mẫu.
    
    Thông tin mỗi chuồng:
    | Tên | Số gà | Sức chứa | Diện tích | Vị trí |
    |-----|------|---------|---------|--------|
    | Chuồng A | 480 | 500 | 50m² | Tầng 1 - Khu A |
    | Chuồng B | 450 | 500 | 50m² | Tầng 1 - Khu B |
    | Chuồng C | 420 | 500 | 50m² | Tầng 2 - Khu A |
    | Chuồng D | 500 | 500 | 50m² | Tầng 2 - Khu B |
    | Chuồng E | 380 | 500 | 50m² | Tầng 3 - Khu A |
    
    Ngưỡng cảnh báo mặc định:
    - Nhiệt độ: 20-30°C
    - Độ ẩm: 50-80%
    - Thức ăn: 20%
    - Nước: 20%
    """
    print("  Đang tạo 5 chuồng gà...")
    
    # Danh sách thông tin chuồng (tên, số gà hiện tại, vị trí)
    coop_data = [
        {'name': 'Chuồng A', 'current_count': 480, 'location': 'Tầng 1 - Khu A'},
        {'name': 'Chuồng B', 'current_count': 450, 'location': 'Tầng 1 - Khu B'},
        {'name': 'Chuồng C', 'current_count': 420, 'location': 'Tầng 2 - Khu A'},
        {'name': 'Chuồng D', 'current_count': 500, 'location': 'Tầng 2 - Khu B'},
        {'name': 'Chuồng E', 'current_count': 380, 'location': 'Tầng 3 - Khu A'},
    ]
    
    coops = []
    
    for data in coop_data:
        # Kiểm tra nếu chuồng đã tồn tại thì bỏ qua
        existing = Coop.query.filter_by(name=data['name']).first()
        if existing:
            print(f"    [Bỏ qua] {data['name']} đã tồn tại")
            coops.append(existing)
            continue
        
        # Tạo chuồng mới với các thông số mặc định
        coop = Coop(
            name=data['name'],
            location=data['location'],
            capacity=500,           # Sức chứa tối đa: 500 gà
            current_count=data['current_count'],  # Số gà hiện tại
            area=50.0,               # Diện tích: 50m²
            
            # Ngưỡng nhiệt độ: 20-30°C
            temp_min=20.0,
            temp_max=30.0,
            
            # Ngưỡng độ ẩm: 50-80%
            humidity_min=50.0,
            humidity_max=80.0,
            
            # Ngưỡng thức ăn và nước: 20%
            feed_threshold=20.0,
            water_threshold=20.0,
            
            # Lịch cho ăn mặc định: 06:00, 12:00, 18:00
            # Sử dụng datetime.strptime để chuyển string thành Time object
            feed_time_1=datetime.strptime('06:00', '%H:%M').time(),
            feed_time_2=datetime.strptime('12:00', '%H:%M').time(),
            feed_time_3=datetime.strptime('18:00', '%H:%M').time(),
            
            # Chế độ tự động: bật tất cả
            auto_fan=True,
            auto_light=True,
            auto_feed=True,
            auto_water=True,
            
            # Trạng thái: đang hoạt động
            status='active'
        )
        
        db.session.add(coop)
        coops.append(coop)
        print(f"    [OK] {coop.name} - {coop.current_count} gà")
    
    db.session.commit()
    return coops


# =============================================================================
# SEED DỮ LIỆU THIẾT BỊ IOT
# =============================================================================

def seed_devices(coops):
    """
    Tạo 15 thiết bị IoT (3 thiết bị/ chuồng).
    
    Mỗi chuồng được gán:
    - 01 Cảm biến nhiệt độ (type: temperature)
    - 01 Cảm biến độ ẩm (type: humidity)
    - 01 Thiết bị điều khiển (type: fan hoặc light)
    
    Trạng thái thiết bị (status) được phân bổ ngẫu nhiên:
    - online: Đang kết nối
    - offline: Không kết nối
    - connecting: Đang kết nối
    
    Loại thiết bị (type):
    - temperature: Cảm biến nhiệt độ
    - humidity: Cảm biến độ ẩm
    - fan: Quạt thông gió
    - light: Đèn chiếu sáng
    """
    print("  Đang tạo 15 thiết bị IoT...")
    
    # Các loại trạng thái kết nối
    statuses = ['online', 'offline', 'connecting']
    
    # Các loại thiết bị điều khiển
    control_types = ['fan', 'light']
    
    devices = []
    device_index = 1  # Số thứ tự thiết bị (để tạo tên duy nhất)
    
    for coop in coops:
        # Tạo 3 thiết bị cho mỗi chuồng
        
        # 1. Cảm biến nhiệt độ
        temp_device = Device(
            name=f'Cảm biến nhiệt {coop.name[-1]}',
            type='temperature',
            mac_address=f'AA:BB:CC:DD:EE:{str(device_index).zfill(2)}',
            status=random.choice(statuses),  # Trạng thái ngẫu nhiên
            is_active=True,
            battery=random.randint(60, 100)  # Pin: 60-100%
        )
        db.session.add(temp_device)
        devices.append(temp_device)
        device_index += 1
        
        # 2. Cảm biến độ ẩm
        humid_device = Device(
            name=f'Cảm biến ẩm {coop.name[-1]}',
            type='humidity',
            mac_address=f'AA:BB:CC:DD:EE:{str(device_index).zfill(2)}',
            status=random.choice(statuses),
            is_active=True,
            battery=random.randint(60, 100)
        )
        db.session.add(humid_device)
        devices.append(humid_device)
        device_index += 1
        
        # 3. Thiết bị điều khiển (quạt hoặc đèn)
        control_type = random.choice(control_types)
        control_name = 'Quạt thông gió' if control_type == 'fan' else 'Đèn LED'
        control_device = Device(
            name=f'{control_name} {coop.name[-1]}',
            type=control_type,
            mac_address=f'AA:BB:CC:DD:EE:{str(device_index).zfill(2)}',
            status=random.choice(statuses),
            is_active=True,
            battery=random.randint(60, 100)
        )
        db.session.add(control_device)
        devices.append(control_device)
        device_index += 1
        
        print(f"    [OK] {coop.name}: 3 thiết bị đã tạo")
    
    db.session.commit()
    return devices


# =============================================================================
# GÁN THIẾT BỊ VÀO CHUỒNG (Bảng trung gian CoopDevice)
# =============================================================================

def seed_coop_devices(coops, devices):
    """
    Gán thiết bị vào các chuồng thông qua bảng trung gian CoopDevice.
    
    Bảng CoopDevice thiết lập quan hệ Many-to-Many giữa Coop và Device.
    Mỗi bản ghi cho biết thiết bị nào đang hoạt động trong chuồng nào.
    """
    print("  Đang gán thiết bị vào chuồng...")
    
    device_idx = 0  # Chỉ số thiết bị trong danh sách devices
    
    for coop in coops:
        # Mỗi chuồng có 3 thiết bị (theo thứ tự: temp, humid, control)
        for i in range(3):
            # Kiểm tra nếu đã tồn tại thì bỏ qua
            existing = CoopDevice.query.filter_by(
                coop_id=coop.id,
                device_id=devices[device_idx].id
            ).first()
            
            if not existing:
                coop_device = CoopDevice(
                    coop_id=coop.id,
                    device_id=devices[device_idx].id
                )
                db.session.add(coop_device)
            
            device_idx += 1
    
    db.session.commit()
    print("    [OK] Đã gán thiết bị vào chuồng")


# =============================================================================
# SEED DỮ LIỆU MÔI TRƯỜNG
# =============================================================================

def seed_environments(coops):
    """
    Tạo dữ liệu môi trường cho 24 giờ qua.
    
    Mỗi chuồng tạo 20 bản ghi cách nhau khoảng 1.2 giờ.
    Dữ liệu bao gồm:
    - Nhiệt độ: 22-28°C (biến đổi tự nhiên trong ngày)
    - Độ ẩm: 55-75%
    - Mức thức ăn: 30-90%
    - Mức nước: 40-95%
    
    Giá trị được random với một chút biến đổi ngẫu nhiên để mô phỏng
    dữ liệu cảm biến thực tế.
    """
    print("  Đang tạo dữ liệu môi trường (20 bản ghi/ chuồng)...")
    
    # Thời gian hiện tại
    now = datetime.utcnow()
    
    for coop in coops:
        # Tạo 20 bản ghi cho mỗi chuồng
        for i in range(20):
            # Thời gian ghi nhận: cách đều trong 24 giờ qua
            # i=0: 24 giờ trước, i=19: hiện tại
            hours_ago = 24 - (i * 1.2)
            recorded_at = now - timedelta(hours=hours_ago)
            
            # Tạo giá trị cảm biến với biến đổi nhẹ
            # Base temperature: 25°C với ±3°C biến đổi
            temperature = random.uniform(22.0, 28.0)
            
            # Base humidity: 65% với ±10% biến đổi
            humidity = random.uniform(55.0, 75.0)
            
            # Feed level: 60% với ±30% biến đổi
            feed_level = random.uniform(30.0, 90.0)
            
            # Water level: 70% với ±30% biến đổi
            water_level = random.uniform(40.0, 95.0)
            
            env = Environment(
                coop_id=coop.id,
                temperature=round(temperature, 1),
                humidity=round(humidity, 1),
                feed_level=round(feed_level, 1),
                water_level=round(water_level, 1),
                recorded_at=recorded_at
            )
            db.session.add(env)
        
        print(f"    [OK] {coop.name}: 20 bản ghi môi trường")
    
    db.session.commit()


# =============================================================================
# SEED LỊCH CHO ĂN
# =============================================================================

def seed_feed_schedules(coops):
    """
    Tạo lịch cho ăn tự động cho mỗi chuồng.
    
    Mỗi chuồng có 3 mốc gi�� cố định:
    - 06:00: Cho ăn sáng (10kg)
    - 12:00: Cho ăn trưa (10kg)
    - 18:00: Cho ăn chiều (10kg)
    
    Tất cả lịch được bật (enabled=True) theo mặc định.
    """
    print("  Đang tạo lịch cho ăn (3 mốc/ chuồng)...")
    
    # Danh sách giờ cho ăn cố định
    feed_times = [
        (datetime.strptime('06:00', '%H:%M').time(), 'Sáng'),
        (datetime.strptime('12:00', '%H:%M').time(), 'Trưa'),
        (datetime.strptime('18:00', '%H:%M').time(), 'Chiều'),
    ]
    
    for coop in coops:
        for feed_time, label in feed_times:
            # Kiểm tra nếu đã tồn tại thì bỏ qua
            existing = FeedSchedule.query.filter_by(
                coop_id=coop.id,
                time=feed_time
            ).first()
            
            if not existing:
                schedule = FeedSchedule(
                    coop_id=coop.id,
                    time=feed_time,
                    amount=10.0,  # Lượng thức ăn: 10kg
                    enabled=True   # Bật lịch cho ăn
                )
                db.session.add(schedule)
        
        print(f"    [OK] {coop.name}: 3 lịch cho ăn (06:00, 12:00, 18:00)")
    
    db.session.commit()


# =============================================================================
# SEED CẢNH BÁO MẪU
# =============================================================================

def seed_alerts(coops):
    """
    Tạo một số cảnh báo mẫu để demo.
    
    Cảnh báo được tạo ngẫu nhiên với các loại:
    - temperature: Cảnh báo nhiệt độ cao/thấp
    - humidity: Cảnh báo độ ẩm cao/thấp
    - device: Cảnh báo thiết bị
    
    Mức độ cảnh báo (level):
    - info: Thông tin
    - warning: Cảnh báo
    - critical: Nghiêm trọng
    """
    print("  Đang tạo cảnh báo mẫu...")
    
    # Template cảnh báo
    alert_templates = [
        {'type': 'temperature', 'level': 'warning', 
         'message': 'Nhiệt độ chuồng cao hơn ngưỡng cho phép'},
        {'type': 'humidity', 'level': 'info', 
         'message': 'Độ ẩm trong chuồng ở mức ổn định'},
        {'type': 'device', 'level': 'warning', 
         'message': 'Cảm biến nhiệt độ mất kết nối tạm thời'},
        {'type': 'feed', 'level': 'info', 
         'message': 'Mức thức ăn còn 30%, cần bổ sung'},
    ]
    
    # Tạo 3 cảnh báo ngẫu nhiên cho mỗi chuồng
    for coop in coops:
        for _ in range(3):
            template = random.choice(alert_templates)
            alert = Alert(
                coop_id=coop.id,
                type=template['type'],
                level=template['level'],
                message=f"{coop.name}: {template['message']}",
                is_resolved=random.choice([True, False])  # Ngẫu nhiên đã xử lý hoặc chưa
            )
            db.session.add(alert)
    
    db.session.commit()
    print("    [OK] Đã tạo cảnh báo mẫu")


# =============================================================================
# XÓA DỮ LIỆU CŨ (RESET DATABASE)
# =============================================================================

def reset_database():
    """
    Xóa tất cả dữ liệu cũ trước khi seed dữ liệu mới.
    
    Thứ tự xóa rất quan trọng để tránh lỗi Foreign Key:
    1. Alert (phụ thuộc Coop, Device)
    2. Environment (phụ thuộc Coop)
    3. FeedSchedule (phụ thuộc Coop)
    4. CoopDevice (phụ thuộc Coop, Device)
    5. Device (độc lập sau khi xóa CoopDevice)
    6. Coop (độc lập sau khi xóa các bảng phụ thuộc)
    7. User (độc lập)
    """
    print("\n[1] Đang xóa dữ liệu cũ...")
    
    # Xóa theo thứ tự để tránh vi phạm ràng buộc khóa ngoài
    print("    Xóa Alert...")
    Alert.query.delete()
    
    print("    Xóa Environment...")
    Environment.query.delete()
    
    print("    Xóa FeedSchedule...")
    FeedSchedule.query.delete()
    
    print("    Xóa CoopDevice...")
    CoopDevice.query.delete()
    
    print("    Xóa Device...")
    Device.query.delete()
    
    print("    Xóa Coop...")
    Coop.query.delete()
    
    print("    Xóa User...")
    User.query.delete()
    
    # Commit sau khi xóa tất cả
    db.session.commit()
    print("    [OK] Đã xóa toàn bộ dữ liệu cũ")


# =============================================================================
# HÀM CHÍNH - CHẠY SEED
# =============================================================================

def run_seed():
    """Hàm chính để chạy toàn bộ quá trình seed dữ liệu."""
    
    # Tạo ứng dụng Flask
    app = create_app()
    
    # Chạy trong application context để có quyền truy cập database
    with app.app_context():
        
        print("=" * 60)
        print("  SEED DỮ LIỆU - HỆ THỐNG QUẢN LÝ TRANG TRẠI GÀ")
        print("=" * 60)
        
        # Tạo bảng database nếu chưa tồn tại
        print("\n[0] Đang tạo bảng database...")
        db.create_all()
        print("    [OK] Bảng database đã sẵn sàng")
        
        # Bước 1: Xóa dữ liệu cũ
        reset_database()
        
        # Bước 2: Seed Users
        print("\n[2] Seed Users...")
        admin = seed_users()
        
        # Bước 3: Seed Coops
        print("\n[3] Seed Coops...")
        coops = seed_coops()
        
        # Bước 4: Seed Devices
        print("\n[4] Seed Devices...")
        devices = seed_devices(coops)
        
        # Bước 5: Seed CoopDevices (gán thiết bị vào chuồng)
        print("\n[5] Seed CoopDevices...")
        seed_coop_devices(coops, devices)
        
        # Bước 6: Seed Environments
        print("\n[6] Seed Environments...")
        seed_environments(coops)
        
        # Bước 7: Seed FeedSchedules
        print("\n[7] Seed FeedSchedules...")
        seed_feed_schedules(coops)
        
        # Bước 8: Seed Alerts
        print("\n[8] Seed Alerts...")
        seed_alerts(coops)
        
        # In thống kê
        print("\n" + "=" * 60)
        print("  THỐNG KÊ DỮ LIỆU SAU KHI SEED")
        print("=" * 60)
        print(f"  Users:        {User.query.count()}")
        print(f"  Coops:        {Coop.query.count()}")
        print(f"  Devices:      {Device.query.count()}")
        print(f"  CoopDevices:  {CoopDevice.query.count()}")
        print(f"  Environments: {Environment.query.count()}")
        print(f"  FeedSchedules: {FeedSchedule.query.count()}")
        print(f"  Alerts:       {Alert.query.count()}")
        print("=" * 60)
        
        print("\n[OK] Seed dữ liệu hoàn tất thành công!")
        print("\nThông tin đăng nhập:")
        print("  Username: admin")
        print("  Password: admin123")


# =============================================================================
# CHẠY SCRIPT
# =============================================================================

if __name__ == '__main__':
    run_seed()