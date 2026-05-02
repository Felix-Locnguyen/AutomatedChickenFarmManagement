"""
Feed Schedule Routes - API quản lý lịch cho ăn

Module này cung cấp các endpoint CRUD cho lịch cho ăn tự động:
- GET /api/feed-schedule: Lấy danh sách lịch (lọc theo coop_id)
- POST /api/feed-schedule: Tạo lịch mới
- PUT /api/feed-schedule/<id>: Cập nhật lịch
- DELETE /api/feed-schedule/<id>: Xóa lịch

Mỗi lịch gắn với một chuồng (coop_id), có giờ cho ăn và lượng thức ăn.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import FeedSchedule, Coop


feed_schedule_bp = Blueprint('feed_schedule', __name__)


@feed_schedule_bp.route('', methods=['GET'])
@jwt_required()
def get_feed_schedules():
    """
    Lấy danh sách lịch cho ăn.

    Query params:
        coop_id (int, optional): Lọc theo chuồng

    Returns:
        200: Array of feed schedule objects
    """
    coop_id = request.args.get('coop_id', type=int)

    if coop_id:
        schedules = FeedSchedule.query.filter_by(coop_id=coop_id).all()
    else:
        schedules = FeedSchedule.query.all()

    return jsonify([s.to_dict() for s in schedules]), 200


@feed_schedule_bp.route('', methods=['POST'])
@jwt_required()
def create_feed_schedule():
    """
    Tạo lịch cho ăn mới.

    Args:
        Request Body (JSON):
            - coop_id (int): ID chuồng (bắt buộc)
            - time (str): Giờ cho ăn, định dạng "HH:MM" (bắt buộc)
            - amount (float): Lượng thức ăn kg (mặc định: 10.0)
            - enabled (bool): Bật/tắt (mặc định: True)

    Returns:
        201: FeedSchedule object đã tạo
        400: Thiếu coop_id hoặc time
        404: Không tìm thấy chuồng
    """
    data = request.get_json()

    coop_id = data.get('coop_id')
    time_str = data.get('time')

    if not coop_id or not time_str:
        return jsonify({'error': 'coop_id and time required'}), 400

    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404

    try:
        time_obj = datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400

    from api import db
    schedule = FeedSchedule(
        coop_id=coop_id,
        time=time_obj,
        amount=data.get('amount', 10.0),
        enabled=data.get('enabled', True)
    )
    db.session.add(schedule)
    db.session.commit()

    return jsonify(schedule.to_dict()), 201


@feed_schedule_bp.route('/<int:schedule_id>', methods=['PUT'])
@jwt_required()
def update_feed_schedule(schedule_id):
    """
    Cập nhật lịch cho ăn.

    Args:
        schedule_id (int): ID lịch
        Request Body (JSON):
            - time (str): Giờ mới "HH:MM"
            - amount (float): Lượng mới (kg)
            - enabled (bool): Bật/tắt

    Returns:
        200: FeedSchedule object đã cập nhật
        404: Không tìm thấy lịch
    """
    schedule = FeedSchedule.query.get(schedule_id)
    if not schedule:
        return jsonify({'error': 'Feed schedule not found'}), 404

    data = request.get_json()

    if 'time' in data:
        try:
            schedule.time = datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400

    if 'amount' in data:
        schedule.amount = data['amount']

    if 'enabled' in data:
        schedule.enabled = data['enabled']

    from api import db
    db.session.commit()

    return jsonify(schedule.to_dict()), 200


@feed_schedule_bp.route('/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
def delete_feed_schedule(schedule_id):
    """
    Xóa lịch cho ăn.

    Args:
        schedule_id (int): ID lịch

    Returns:
        200: Thông báo thành công
        404: Không tìm thấy lịch
    """
    schedule = FeedSchedule.query.get(schedule_id)
    if not schedule:
        return jsonify({'error': 'Feed schedule not found'}), 404

    from api import db
    db.session.delete(schedule)
    db.session.commit()

    return jsonify({'message': 'Feed schedule deleted'}), 200