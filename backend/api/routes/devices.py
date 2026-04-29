"""
Devices Routes - API quản lý thiết bị IoT

Module này cung cấp các endpoint cho việc:
- CRUD thiết bị (Create, Read, Update, Delete)
- Kết nối thiết bị mới (quét QR / nhập mã)
- Bật/tắt thiết bị
- Gán thiết bị vào chuồng
- Cập nhật tên thiết bị sau khi kết nối thành công

Các loại thiết bị được hỗ trợ:
- sensor: Cảm biến (nhiệt độ, độ ẩm)
- fan: Quạt
- light: Đèn
- feeder: Hệ thống cho ăn
- camera: Camera

Trạng thái thiết bị:
- online: Đang kết nối và hoạt động
- offline: Không kết nối
- connecting: Đang trong quá trình kết nối
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

# Thêm đường dẫn parent vào sys.path để có thể import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import Device, CoopDevice

# Tạo Blueprint cho routes liên quan đến thiết bị
# URL: /api/devices
devices_bp = Blueprint('devices', __name__)


@devices_bp.route('', methods=['GET'])
@jwt_required()
def get_devices():
    """
    Lấy danh sách tất cả thiết bị.
    
    Returns:
        200: Array of device objects
        401: Unauthorized
    """
    devices = Device.query.all()
    return jsonify([device.to_dict() for device in devices]), 200


@devices_bp.route('', methods=['POST'])
@jwt_required()
def create_device():
    """
    Tạo thiết bị mới (thủ công).
    
    Thường dùng để thêm thiết bị thủ công vào hệ thống,
    không phải qua flow kết nối thiết bị tự động.
    
    Args:
        Request Body (JSON):
            - name (str): Tên thiết bị
            - type (str): Loại thiết bị (sensor/fan/light/feeder/camera)
            - mac_address (str): Địa chỉ MAC
            - status (str): Trạng thái (online/offline/connecting)
            - is_active (bool): Bật/tắt
            - battery (int): % pin
            
    Returns:
        201: Device object đã tạo
    """
    data = request.get_json()
    
    device = Device(
        name=data.get('name'),
        type=data.get('type', 'sensor'),
        mac_address=data.get('mac_address', ''),
        status=data.get('status', 'offline'),
        is_active=data.get('is_active', True),
        battery=data.get('battery', 100)
    )
    
    from api import db
    db.session.add(device)
    db.session.commit()
    
    return jsonify(device.to_dict()), 201


@devices_bp.route('/connect', methods=['POST'])
@jwt_required()
def connect_device():
    """
    Kết nối thiết bị mới.
    
    Đây là endpoint chính cho flow thêm thiết bị từ frontend:
    1. User quét QR hoặc nhập mã thiết bị
    2. Gọi API này với device_id (từ QR/mã)
    3. Nếu thiết bị chưa tồn tại -> tạo mới với status 'connecting'
    4. Nếu thiết bị đã tồn tại -> chuyển status thành 'connecting'
    
    Args:
        Request Body (JSON):
            - device_id (str): ID thiết bị hoặc MAC address
            
    Returns:
        200: {
            "message": "Device connecting",
            "device": {...},
            "status": "connecting"
        }
        400: Thiếu device_id hoặc thiết bị đã online
    """
    data = request.get_json()
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id required'}), 400
    
    # Tìm thiết bị theo ID hoặc MAC address
    device = Device.query.filter(
        (Device.id == device_id) | 
        (Device.mac_address == device_id)
    ).first()
    
    # Nếu chưa có -> tạo mới
    if not device:
        device = Device(
            name=f"Device {device_id}",
            mac_address=device_id,
            type='sensor',
            status='connecting',  # Trạng thái đang kết nối
            is_active=True,
            battery=100
        )
        from api import db
        db.session.add(device)
        db.session.commit()
        return jsonify({
            'message': 'Device connecting', 
            'device': device.to_dict(),
            'status': 'connecting'
        }), 200
    
    # Kiểm tra thiết bị đã kết nối chưa
    if device.status == 'online':
        return jsonify({'error': 'Device already connected', 'device': device.to_dict()}), 400
    
    # Cập nhật trạng thái sang connecting
    device.status = 'connecting'
    from api import db
    db.session.commit()
    
    return jsonify({
        'message': 'Device connecting', 
        'device': device.to_dict(),
        'status': 'connecting'
    }), 200


@devices_bp.route('/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device(device_id):
    """
    Lấy thông tin một thiết bị cụ thể.
    
    Args:
        device_id (int): ID của thiết bị
        
    Returns:
        200: Device object
        404: Không tìm thấy thiết bị
    """
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify(device.to_dict()), 200


@devices_bp.route('/<int:device_id>', methods=['PUT'])
@jwt_required()
def update_device(device_id):
    """
    Cập nhật thông tin thiết bị.
    
    Args:
        device_id (int): ID của thiết bị
        Request Body: Các trường cần cập nhật
        
    Returns:
        200: Device object đã cập nhật
        404: Không tìm thấy thiết bị
    """
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.get_json()
    
    device.name = data.get('name', device.name)
    device.type = data.get('type', device.type)
    device.mac_address = data.get('mac_address', device.mac_address)
    device.status = data.get('status', device.status)
    device.is_active = data.get('is_active', device.is_active)
    device.battery = data.get('battery', device.battery)
    
    from api import db
    db.session.commit()
    
    return jsonify(device.to_dict()), 200


@devices_bp.route('/<int:device_id>', methods=['DELETE'])
@jwt_required()
def delete_device(device_id):
    """
    Xóa thiết bị.
    
    Xóa thiết bị sẽ đồng thời xóa các liên kết trong CoopDevice.
    
    Args:
        device_id (int): ID của thiết bị
        
    Returns:
        200: Thông báo thành công
        404: Không tìm thấy thiết bị
    """
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    from api import db
    
    # Xóa các liên kết với chuồng trước
    CoopDevice.query.filter_by(device_id=device_id).delete()
    # Xóa thiết bị
    db.session.delete(device)
    db.session.commit()
    
    return jsonify({'message': 'Device deleted'}), 200


@devices_bp.route('/<int:device_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_device(device_id):
    """
    Bật/tắt thiết bị.
    
    Chuyển đổi trạng thái is_active của thiết bị.
    
    Args:
        device_id (int): ID của thiết bị
        
    Returns:
        200: {
            "message": "Device toggled",
            "is_active": true/false,
            "device": {...}
        }
        404: Không tìm thấy thiết bị
    """
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    # Toggle is_active
    device.is_active = not device.is_active
    
    from api import db
    db.session.commit()
    
    return jsonify({
        'message': 'Device toggled',
        'is_active': device.is_active,
        'device': device.to_dict()
    }), 200


@devices_bp.route('/<int:device_id>/assign', methods=['POST'])
@jwt_required()
def assign_device_to_coop(device_id):
    """
    Gán thiết bị vào chuồng.
    
    Tạo liên kết trong bảng CoopDevice để kết nối
    thiết bị với chuồng.
    
    Args:
        device_id (int): ID của thiết bị
        Request Body (JSON):
            - coop_id (int): ID của chuồng
            
    Returns:
        200: Thông báo thành công
        400: Thiếu coop_id hoặc đã gán rồi
        404: Không tìm thấy thiết bị/chuồng
    """
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.get_json()
    coop_id = data.get('coop_id')
    
    if not coop_id:
        return jsonify({'error': 'coop_id required'}), 400
    
    from api import db
    from models import Coop
    
    # Kiểm tra chuồng tồn tại
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404
    
    # Kiểm tra đã gán chưa
    existing = CoopDevice.query.filter_by(coop_id=coop_id, device_id=device_id).first()
    if existing:
        return jsonify({'error': 'Device already assigned to this coop'}), 400
    
    # Tạo liên kết mới
    coop_device = CoopDevice(coop_id=coop_id, device_id=device_id, is_active=True)
    db.session.add(coop_device)
    db.session.commit()
    
    return jsonify({'message': 'Device assigned to coop', 'coop_device': {
        'coop_id': coop_id,
        'device_id': device_id,
        'is_active': True
    }}), 200


@devices_bp.route('/<int:device_id>/name', methods=['PATCH'])
@jwt_required()
def update_device_name(device_id):
    """
    Cập nhật tên thiết bị sau khi kết nối thành công.
    
    Đây là endpoint cuối cùng trong flow kết nối thiết bị:
    1. connect_device -> status: 'connecting'
    2. (thiết bị thực tế kết nối thành công)
    3. update_device_name -> status: 'online', cập nhật tên
    
    Args:
        device_id (int): ID của thiết bị
        Request Body (JSON):
            - name (str): Tên mới cho thiết bị
            
    Returns:
        200: Device object đã cập nhật
        400: Thiếu name
        404: Không tìm thấy thiết bị
    """
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'name required'}), 400
    
    # Cập nhật tên và đánh dấu đã kết nối
    device.name = name
    device.status = 'online'
    
    from api import db
    db.session.commit()
    
    return jsonify({
        'message': 'Device name updated',
        'device': device.to_dict()
    }), 200