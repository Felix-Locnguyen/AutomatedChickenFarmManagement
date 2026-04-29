"""
Dashboard Routes - API thống kê và tổng quan hệ thống

Module này cung cấp các endpoint cho việc:
- Lấy tổng quan dashboard (số lượng chuồng, thiết bị, trạng thái)
- Thống kê chi tiết (số gà, sức chứa, trạng thái chuồng)
- Lấy danh sách cảnh báo
- Lấy hoạt động gần đây

Dữ liệu được tổng hợp từ nhiều bảng: Coop, Device, Environment, Alert
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import Coop, Device, CoopDevice, Environment, Alert

# Tạo Blueprint cho routes dashboard
# URL: /api/dashboard
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def get_dashboard():
    """
    Lấy tổng quan dashboard.
    
    Trả về thông tin tổng hợp về:
    - Số lượng chuồng, thiết bị
    - Số thiết bị online/offline/connecting
    - Nhiệt độ và độ ẩm trung bình
    - Danh sách chuồng với trạng thái
    
    Returns:
        200: {
            "total_coops": 5,
            "total_devices": 20,
            "online_devices": 15,
            "offline_devices": 3,
            "connecting_devices": 2,
            "avg_temperature": 25.5,
            "avg_humidity": 65.2,
            "coops": [...],
            "timestamp": "2025-01-01T00:00:00"
        }
    """
    coops = Coop.query.all()
    devices = Device.query.all()
    
    # Thống kê cơ bản
    total_coops = len(coops)
    total_devices = len(devices)
    online_devices = len([d for d in devices if d.status == 'online'])
    offline_devices = len([d for d in devices if d.status == 'offline'])
    connecting_devices = len([d for d in devices if d.status == 'connecting'])
    
    # Tính trung bình nhiệt độ và độ ẩm
    avg_temperature = 0
    avg_humidity = 0
    coop_stats = []
    
    for coop in coops:
        # Lấy dữ liệu môi trường mới nhất của chuồng
        env = Environment.query.filter_by(coop_id=coop.id).order_by(Environment.recorded_at.desc()).first()
        
        if env:
            avg_temperature += env.temperature or 0
            avg_humidity += env.humidity or 0
        
        # Đếm số thiết bị trong chuồng
        coop_devices = CoopDevice.query.filter_by(coop_id=coop.id).count()
        
        # Thêm vào danh sách thống kê
        coop_stats.append({
            'id': coop.id,
            'name': coop.name,
            'current_count': coop.current_count,
            'capacity': coop.capacity,
            'status': coop.status,
            'device_count': coop_devices,
            'temperature': env.temperature if env else None,
            'humidity': env.humidity if env else None
        })
    
    # Tính trung bình
    if total_coops > 0:
        avg_temperature /= total_coops
        avg_humidity /= total_coops
    
    return jsonify({
        'total_coops': total_coops,
        'total_devices': total_devices,
        'online_devices': online_devices,
        'offline_devices': offline_devices,
        'connecting_devices': connecting_devices,
        'avg_temperature': round(avg_temperature, 1),
        'avg_humidity': round(avg_humidity, 1),
        'coops': coop_stats,
        'timestamp': datetime.now().isoformat()
    }), 200


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    Lấy thống kê chi tiết.
    
    Bao gồm:
    - Tổng số gà và sức chứa
    - Tỷ lệ sử dụng sức chứa
    - Số lượng chuồng theo trạng thái (normal/warning/error)
    - Số lượng thiết bị theo loại
    
    Returns:
        200: {
            "total_chickens": 2500,
            "total_capacity": 2500,
            "capacity_usage": 100.0,
            "coop_status": {"normal": 3, "warning": 1, "error": 1},
            "device_type_count": {"sensor": 10, "fan": 5, "light": 3, "camera": 2}
        }
    """
    coops = Coop.query.all()
    devices = Device.query.all()
    
    # Tổng số gà và sức chứa
    chicken_count = sum(c.current_count for c in coops)
    total_capacity = sum(c.capacity for c in coops)
    
    # Thống kê trạng thái chuồng
    coop_status = {
        'normal': len([c for c in coops if c.status == 'normal']),
        'warning': len([c for c in coops if c.status == 'warning']),
        'error': len([c for c in coops if c.status == 'error'])
    }
    
    # Thống kê thiết bị theo loại
    device_type_count = {}
    for device in devices:
        device_type_count[device.type] = device_type_count.get(device.type, 0) + 1
    
    return jsonify({
        'total_chickens': chicken_count,
        'total_capacity': total_capacity,
        'capacity_usage': round(chicken_count / total_capacity * 100, 1) if total_capacity > 0 else 0,
        'coop_status': coop_status,
        'device_type_count': device_type_count
    }), 200


@dashboard_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """
    Lấy danh sách cảnh báo chưa xử lý.
    
    Chỉ lấy các cảnh báo có is_resolved = False,
    sắp xếp theo thời gian giảm dần (mới nhất trước).
    
    Query params:
        limit (int): Số lượng cảnh báo (mặc định: 10)
    
    Returns:
        200: Array of alert objects
    """
    limit = 10
    alerts = Alert.query.filter_by(is_resolved=False).order_by(Alert.created_at.desc()).limit(limit).all()
    
    return jsonify([alert.to_dict() for alert in alerts]), 200


@dashboard_bp.route('/recent-activities', methods=['GET'])
@jwt_required()
def get_recent_activities():
    """
    Lấy các hoạt động gần đây.
    
    Tổng hợp các hoạt động từ:
    - Dữ liệu môi trường mới nhất của các chuồng
    
    Returns:
        200: [
            {
                "type": "environment",
                "coop": "Chuồng A",
                "temperature": 26.5,
                "humidity": 68.0,
                "timestamp": "2025-01-01T00:00:00"
            },
            ...
        ]
    """
    activities = []
    
    # Lấy 5 bản ghi môi trường mới nhất
    recent_environments = Environment.query.order_by(Environment.recorded_at.desc()).limit(5).all()
    for env in recent_environments:
        coop = Coop.query.get(env.coop_id)
        activities.append({
            'type': 'environment',
            'coop': coop.name if coop else 'Unknown',
            'temperature': env.temperature,
            'humidity': env.humidity,
            'timestamp': env.recorded_at.isoformat() if env.recorded_at else None
        })
    
    return jsonify(activities), 200