"""
Coops Routes - API quản lý chuồng trại

Module này cung cấp các endpoint cho việc:
- CRUD chuồng trại (Create, Read, Update, Delete)
- Quản lý thiết bị trong chuồng
- Lấy dữ liệu môi trường (nhiệt độ, độ ẩm,...)
- Lịch sử dữ liệu theo thời gian

Mỗi chuồng có thể chứa nhiều thiết bị và có các thông số môi trường riêng.
Các thông số cảnh báo (ngưỡng nhiệt độ, độ ẩm,...) được cấu hình cho từng chuồng.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

# Thêm đường dẫn parent vào sys.path để có thể import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import Coop, CoopDevice, Device, Environment

# Tạo Blueprint cho routes liên quan đến chuồng
# URL: /api/coops
coops_bp = Blueprint('coops', __name__)


@coops_bp.route('', methods=['GET'])
@jwt_required()
def get_coops():
    """
    Lấy danh sách tất cả các chuồng.
    
    Returns:
        200: Array of coop objects
        401: Unauthorized
    """
    coops = Coop.query.all()
    return jsonify([coop.to_dict() for coop in coops]), 200


@coops_bp.route('', methods=['POST'])
@jwt_required()
def create_coop():
    """
    Tạo chuồng mới.
    
    Args:
        Request Body (JSON):
            - name (str): Tên chuồng (bắt buộc)
            - location (str): Địa điểm (tùy chọn)
            - capacity (int): Sức chứa tối đa (mặc định: 500)
            - current_count (int): Số gà hiện tại (mặc định: 0)
            - area (float): Diện tích m² (mặc định: 50)
            - temp_min/max (float): Ngưỡng nhiệt độ
            - humidity_min/max (float): Ngưỡng độ ẩm
            - feed_threshold (int): Ngưỡng thức ăn (%)
            - water_threshold (int): Ngưỡng nước (%)
            - feed_time_1/2/3 (str): Giờ cho ăn
            - auto_fan/light/feed/water (bool): Bật/tắt tự động
        
    Returns:
        201: Coop object đã tạo
        400: Thiếu name
    """
    data = request.get_json()
    
    coop = Coop(
        name=data.get('name'),
        location=data.get('location', ''),
        capacity=data.get('capacity', 500),
        current_count=data.get('current_count', 0),
        area=data.get('area', 50),
        # Ngưỡng cảnh báo nhiệt độ
        temp_min=data.get('temp_min', 18),
        temp_max=data.get('temp_max', 28),
        # Ngưỡng cảnh báo độ ẩm
        humidity_min=data.get('humidity_min', 50),
        humidity_max=data.get('humidity_max', 80),
        # Ngưỡng thức ăn/nước
        feed_threshold=data.get('feed_threshold', 30),
        water_threshold=data.get('water_threshold', 30),
        # Lịch cho ăn tự động
        feed_time_1=data.get('feed_time_1', '06:00'),
        feed_time_2=data.get('feed_time_2', '12:00'),
        feed_time_3=data.get('feed_time_3', '18:00'),
        # Cấu hình tự động hóa
        auto_fan=data.get('auto_fan', True),
        auto_light=data.get('auto_light', True),
        auto_feed=data.get('auto_feed', True),
        auto_water=data.get('auto_water', True),
        status='normal'  # Trạng thái mặc định
    )
    
    from models import db
    db.session.add(coop)
    db.session.commit()
    
    return jsonify(coop.to_dict()), 201


@coops_bp.route('/<int:coop_id>', methods=['GET'])
@jwt_required()
def get_coop(coop_id):
    """
    Lấy thông tin một chuồng cụ thể.
    
    Args:
        coop_id (int): ID của chuồng
        
    Returns:
        200: Coop object
        404: Không tìm thấy chuồng
    """
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404
    return jsonify(coop.to_dict()), 200


@coops_bp.route('/<int:coop_id>', methods=['PUT'])
@jwt_required()
def update_coop(coop_id):
    """
    Cập nhật thông tin chuồng.
    
    Args:
        coop_id (int): ID của chuồng cần cập nhật
        Request Body: Các trường cần cập nhật
        
    Returns:
        200: Coop object đã cập nhật
        404: Không tìm thấy chuồng
    """
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404
    
    data = request.get_json()
    
    # Cập nhật các trường được gửi lên, giữ nguyên giá trị cũ nếu không có
    coop.name = data.get('name', coop.name)
    coop.location = data.get('location', coop.location)
    coop.capacity = data.get('capacity', coop.capacity)
    coop.current_count = data.get('current_count', coop.current_count)
    coop.area = data.get('area', coop.area)
    coop.temp_min = data.get('temp_min', coop.temp_min)
    coop.temp_max = data.get('temp_max', coop.temp_max)
    coop.humidity_min = data.get('humidity_min', coop.humidity_min)
    coop.humidity_max = data.get('humidity_max', coop.humidity_max)
    coop.feed_threshold = data.get('feed_threshold', coop.feed_threshold)
    coop.water_threshold = data.get('water_threshold', coop.water_threshold)
    coop.auto_fan = data.get('auto_fan', coop.auto_fan)
    coop.auto_light = data.get('auto_light', coop.auto_light)
    coop.auto_feed = data.get('auto_feed', coop.auto_feed)
    coop.auto_water = data.get('auto_water', coop.auto_water)
    
    from models import db
    db.session.commit()
    
    return jsonify(coop.to_dict()), 200


@coops_bp.route('/<int:coop_id>', methods=['DELETE'])
@jwt_required()
def delete_coop(coop_id):
    """
    Xóa một chuồng.
    
    Lưu ý: Xóa chuồng sẽ không xóa các thiết bị liên quan,
    chỉ xóa các liên kết trong bảng CoopDevice.
    
    Args:
        coop_id (int): ID của chuồng cần xóa
        
    Returns:
        200: Thông báo thành công
        404: Không tìm thấy chuồng
    """
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404
    
    from models import db
    db.session.delete(coop)
    db.session.commit()
    
    return jsonify({'message': 'Coop deleted'}), 200


@coops_bp.route('/<int:coop_id>/devices', methods=['GET'])
@jwt_required()
def get_coop_devices(coop_id):
    """
    Lấy danh sách thiết bị trong một chuồng.
    
    Sử dụng bảng trung gian CoopDevice để lấy các thiết bị
    được gán vào chuồng.
    
    Args:
        coop_id (int): ID của chuồng
        
    Returns:
        200: Array of device objects
        404: Không tìm thấy chuồng
    """
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404
    
    # Lấy tất cả các link thiết bị-chuồng
    coop_devices = CoopDevice.query.filter_by(coop_id=coop_id).all()
    devices = []
    for cd in coop_devices:
        device = Device.query.get(cd.device_id)
        if device:
            devices.append(device.to_dict())
    
    return jsonify(devices), 200


@coops_bp.route('/<int:coop_id>/environment', methods=['GET'])
@jwt_required()
def get_coop_environment(coop_id):
    """
    Lấy dữ liệu môi trường mới nhất của chu���ng.
    
    Trả về các thông số:
    - temperature: Nhiệt độ (°C)
    - humidity: Độ ẩm (%)
    - feed_level: Mức thức ăn (%)
    - water_level: Mức nước (%)
    - recorded_at: Thời gian ghi nhận
    
    Args:
        coop_id (int): ID của chuồng
        
    Returns:
        200: Environment object mới nhất
        404: Không tìm thấy chuồng hoặc chưa có dữ liệu
    """
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404
    
    # Lấy bản ghi mới nhất, sắp xếp theo thời gian giảm dần
    environment = Environment.query.filter_by(coop_id=coop_id).order_by(Environment.recorded_at.desc()).first()
    
    if not environment:
        return jsonify({'error': 'No environment data'}), 404
    
    return jsonify(environment.to_dict()), 200


@coops_bp.route('/<int:coop_id>/history', methods=['GET'])
@jwt_required()
def get_coop_history(coop_id):
    """
    Lấy lịch sử dữ liệu môi trường của chuồng.
    
    Args:
        coop_id (int): ID của chuồng
        limit (int, query param): Số lượng bản ghi (mặc định: 24)
        
    Returns:
        200: Array of environment objects
        404: Không tìm thấy chuồng
    """
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404
    
    limit = request.args.get('limit', 24, type=int)
    environments = Environment.query.filter_by(coop_id=coop_id).order_by(Environment.recorded_at.desc()).limit(limit).all()
    
    return jsonify([env.to_dict() for env in environments]), 200