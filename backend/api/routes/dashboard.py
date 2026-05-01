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
from sqlalchemy import func
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import Coop, Device, CoopDevice, Environment, Alert, db

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
    - Tổng số chuồng, thiết bị
    - Tổng số gà, sức chứa tổng
    - Số thiết bị đang online
    - Số cảnh báo chưa xử lý
    - Thống kê trạng thái chuồng
    
    Returns:
        200: {
            "total_coops": 5,
            "total_devices": 20,
            "total_chickens": 2500,
            "total_capacity": 2500,
            "online_devices": 15,
            "unresolved_alerts": 3,
            "coop_status": {"active": 3, "cleaning": 1, "empty": 1}
        }
    """
    chicken_count = db.session.query(func.sum(Coop.current_count)).scalar() or 0
    total_capacity = db.session.query(func.sum(Coop.capacity)).scalar() or 0
    online_devices = Device.query.filter(Device.status == 'online').count()
    unresolved_alerts = Alert.query.filter(Alert.is_resolved == False).count()
    
    coop_status = {
        'active': Coop.query.filter(Coop.status == 'active').count(),
        'cleaning': Coop.query.filter(Coop.status == 'cleaning').count(),
        'empty': Coop.query.filter(Coop.status == 'empty').count()
    }
    
    return jsonify({
        'total_coops': Coop.query.count(),
        'total_devices': Device.query.count(),
        'total_chickens': chicken_count,
        'total_capacity': total_capacity,
        'online_devices': online_devices,
        'unresolved_alerts': unresolved_alerts,
        'coop_status': coop_status
    }), 200


@dashboard_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """
    Lấy danh sách cảnh báo mới nhất (mức độ Critical/Warning).
    
    Chỉ lấy các cảnh báo:
    - is_resolved = False
    - level IN ('critical', 'warning')
    - sắp xếp theo thời gian giảm dần (mới nhất trước)
    
    Query params:
        limit (int): Số lượng cảnh báo (mặc định: 10)
    
    Returns:
        200: Array of alert objects
    """
    limit = 10
    alerts = Alert.query.filter(
        Alert.is_resolved == False,
        Alert.level.in_(['critical', 'warning'])
    ).order_by(Alert.created_at.desc()).limit(limit).all()
    
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