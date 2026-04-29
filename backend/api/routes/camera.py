"""
Camera Routes - API quản lý camera

Module này cung cấp các endpoint cho việc:
- Lấy danh sách camera
- Lấy thông tin chi tiết camera
- Lấy camera theo chuồng
- Chụp ảnh snapshot
- Lấy URL stream video
- Lấy danh sách recordings

Camera là một loại thiết bị đặc biệt (type='camera').
Mỗi camera có thể được gán vào một hoặc nhiều chuồng.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import Coop, Device, CoopDevice

# Tạo Blueprint cho routes camera
# URL: /api/camera
camera_bp = Blueprint('camera', __name__)


@camera_bp.route('', methods=['GET'])
@jwt_required()
def get_cameras():
    """
    Lấy danh sách tất cả camera.
    
    Lọc các thiết bị có type='camera' và trả về thông tin
    kèm theo danh sách chuồng mà camera đó được gán.
    
    Returns:
        200: [
            {
                "id": 1,
                "name": "Camera Chuồng A",
                "status": "online",
                "is_active": true,
                "coops": [{"id": 1, "name": "Chuồng A"}]
            },
            ...
        ]
    """
    # Lọc chỉ lấy các thiết bị là camera
    devices = Device.query.filter_by(type='camera').all()
    cameras = []
    
    for device in devices:
        # Lấy danh sách chuồng của camera
        coop_devices = CoopDevice.query.filter_by(device_id=device.id).all()
        coop_ids = [cd.coop_id for cd in coop_devices]
        coops = Coop.query.filter(Coop.id.in_(coop_ids)).all() if coop_ids else []
        
        cameras.append({
            'id': device.id,
            'name': device.name,
            'status': device.status,
            'is_active': device.is_active,
            'coops': [{'id': c.id, 'name': c.name} for c in coops]
        })
    
    return jsonify(cameras), 200


@camera_bp.route('/<int:device_id>', methods=['GET'])
@jwt_required()
def get_camera(device_id):
    """
    Lấy thông tin chi tiết một camera.
    
    Args:
        device_id (int): ID của camera
        
    Returns:
        200: {
            "id": 1,
            "name": "Camera Chuồng A",
            "status": "online",
            "is_active": true,
            "mac_address": "00:11:22:33:44:55",
            "battery": 85,
            "coops": [...],
            "created_at": "2025-01-01T00:00:00"
        }
        404: Không tìm thấy camera
    """
    # Tìm thiết bị là camera
    device = Device.query.filter_by(id=device_id, type='camera').first()
    if not device:
        return jsonify({'error': 'Camera not found'}), 404
    
    # Lấy danh sách chuồng
    coop_devices = CoopDevice.query.filter_by(device_id=device_id).all()
    coop_ids = [cd.coop_id for cd in coop_devices]
    coops = Coop.query.filter(Coop.id.in_(coop_ids)).all() if coop_ids else []
    
    return jsonify({
        'id': device.id,
        'name': device.name,
        'status': device.status,
        'is_active': device.is_active,
        'mac_address': device.mac_address,
        'battery': device.battery,
        'coops': [{'id': c.id, 'name': c.name} for c in coops],
        'created_at': device.created_at.isoformat() if device.created_at else None
    }), 200


@camera_bp.route('/coop/<int:coop_id>', methods=['GET'])
@jwt_required()
def get_camera_by_coop(coop_id):
    """
    Lấy danh sách camera của một chuồng cụ thể.
    
    Args:
        coop_id (int): ID của chuồng
        
    Returns:
        200: [
            {"id": 1, "name": "Camera A1", "status": "online", "is_active": true},
            ...
        ]
        404: Không tìm thấy chuồng
    """
    # Kiểm tra chuồng tồn tại
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404
    
    # Lấy danh sách thiết bị trong chuồng
    coop_devices = CoopDevice.query.filter_by(coop_id=coop_id).all()
    device_ids = [cd.device_id for cd in coop_devices]
    
    # Lọc chỉ lấy camera
    cameras = Device.query.filter(
        Device.id.in_(device_ids),
        Device.type == 'camera'
    ).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'status': c.status,
        'is_active': c.is_active
    } for c in cameras]), 200


@camera_bp.route('/<int:device_id>/snapshot', methods=['POST'])
@jwt_required()
def capture_snapshot(device_id):
    """
    Chụp ảnh snapshot từ camera.
    
    Gửi lệnh yêu cầu camera chụp 1 frame và lưu lại.
    (Đây là API mô phỏng - cần tích hợp với thiết bị thực tế)
    
    Args:
        device_id (int): ID của camera
        
    Returns:
        200: {
            "device_id": 1,
            "device_name": "Camera A1",
            "timestamp": "2025-01-01T00:00:00",
            "success": true,
            "image_url": "/uploads/cameras/1/snapshot.jpg"
        }
        404: Không tìm thấy camera
    """
    device = Device.query.filter_by(id=device_id, type='camera').first()
    if not device:
        return jsonify({'error': 'Camera not found'}), 404
    
    # Mô phỏng snapshot (cần tích hợp với actual camera API)
    snapshot = {
        'device_id': device_id,
        'device_name': device.name,
        'timestamp': datetime.now().isoformat(),
        'success': True,
        'image_url': f'/uploads/cameras/{device_id}/snapshot.jpg'
    }
    
    return jsonify(snapshot), 200


@camera_bp.route('/<int:device_id>/stream', methods=['GET'])
@jwt_required()
def get_stream_url(device_id):
    """
    Lấy URL streaming của camera.
    
    Trả về URL RTSP/HTTP để truy cập video stream.
    (Đây là API mô phỏng - cần tích hợp với thiết bị thực tế)
    
    Args:
        device_id (int): ID của camera
        
    Returns:
        200: {
            "device_id": 1,
            "stream_url": "rtsp://camera-1.local:8554/stream",
            "status": "online"
        }
        404: Không tìm thấy camera
    """
    device = Device.query.filter_by(id=device_id, type='camera').first()
    if not device:
        return jsonify({'error': 'Camera not found'}), 404
    
    # Mô phỏng stream URL (thay bằng actual camera stream URL)
    stream_url = f'rtsp://camera-{device_id}.local:8554/stream'
    
    return jsonify({
        'device_id': device_id,
        'stream_url': stream_url,
        'status': device.status
    }), 200


@camera_bp.route('/<int:device_id>/recordings', methods=['GET'])
@jwt_required()
def get_recordings(device_id):
    """
    Lấy danh sách recordings của camera.
    
    Query params:
        limit (int): Số lượng recordings (mặc định: 10)
    
    Args:
        device_id (int): ID của camera
        
    Returns:
        200: {
            "device_id": 1,
            "recordings": [],
            "count": 0
        }
        404: Không tìm thấy camera
    """
    device = Device.query.filter_by(id=device_id, type='camera').first()
    if not device:
        return jsonify({'error': 'Camera not found'}), 404
    
    limit = request.args.get('limit', 10, type=int)
    
    # Mô phỏng recordings (cần tích hợp với storage thực tế)
    recordings = []
    
    return jsonify({
        'device_id': device_id,
        'recordings': recordings,
        'count': len(recordings)
    }), 200