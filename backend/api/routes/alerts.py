"""
Alert Routes - API quản lý cảnh báo hệ thống
Module này cung cấp các endpoint CRUD cho cảnh báo:
- GET /api/alerts: Danh sách cảnh báo (lọc theo is_resolved, level, coop_ id)
- PUT /api/alerts/<id>/resolve: Đánh dấu cảnh báo đã xử lý
Thông tin chi tiết bao gồm tên chuồng và loại thiết bị gây ra cảnh báo.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, UTC
import sys
import os
sys.path. append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import db, Alert, Coop, Device
alerts_bp = Blueprint('alerts', __name__)


@alerts_bp. route('', methods=['GET'])
@jwt_required()
def get_alerts():
    """
    Lấy danh sách tất cả cảnh báo hệ thống.
    Query params:
        is_resolved (str, optional): Lọc theo trạng thái xử lý ('true'/'false')
        level (str, optional): Lọc theo mức độ (info/warning/critical)
        coop_id (int, optional): Lọc theo chuồng
    Returns:
        200: Array of alert objects với thông tin chi tiết
    """
    is_resolved_str = request.args.get('is_resolved')
    level = request.args.get('level')
    coop_id = request.args.get('coop_id', type=int)
    
    query = Alert.query
    
    # Properly parse is_resolved parameter
    if is_resolved_str is not None:
        is_resolved = is_resolved_str.lower() == 'true'
        query = query.filter(Alert.is_resolved == is_resolved)
    
    if level:
        query = query.filter(Alert.level == level)
    if coop_id:
        query = query.filter(Alert.coop_id == coop_id)
    alerts = query.order_by(Alert.created_at.desc()).all()
    result = []
    for alert in alerts:
        alert_dict = alert.to_dict()
        if alert.coop_id:
            coop = db.session.get(Coop, alert.coop_id)
            alert_dict['coop_name'] = coop.name if coop else None
        if alert.device_id:
            device = db.session.get(Device, alert.device_id)
            alert_dict['device_name'] = device.name if device else None
            alert_dict['device_type'] = device.type if device else None
        result.append(alert_dict)
    return jsonify(result), 200


@alerts_bp.route('/<int:alert_id>/resolve', methods=['PUT'])
@jwt_required()
def resolve_alert(alert_id):
    """
    Đánh dấu một cảnh báo đã được xử lý.
    Args:
        alert_id (int): ID cảnh báo
    Returns:
        200: Alert object đã cập nhật
        404: Không tìm thấy cảnh báo
    """
    alert = db.session.get(Alert, alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    alert.is_resolved = True
    alert.resolved_at = datetime.now(UTC)
    db.session.commit()
    return jsonify(alert.to_dict()), 200