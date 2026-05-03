""" 
Environment Routes - API dữ liệu cảm biến môi trường

Module này xử lý dữ liệu từ cảm biến IoT gửi về:
- POST /api/environment: Nhận dữ liệu từ thiết bị, lưu vào DB
- GET /api/environment/<coop_id>: Thông số môi trường hiện tại
- GET /api/environment/<coop_id>/history: Dữ liệu lịch sử để vẽ biểu đồ

Dữ liệu môi trường: nhiệt độ, độ ẩm, mức thức ăn, mức nước.
Sắp xếp theo thời gian mới nhất (recorded_at DESC).
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models import Environment, Coop

environment_bp = Blueprint('environment', __name__)


@environment_bp.route('', methods=['POST'])
@jwt_required()
def create_environment():
    """
    Nhận dữ liệu môi trường từ thiết bị IoT, lưu vào DB.

    Thiết bị cảm biến gửi dữ liệu định kỳ (nhiệt độ, độ ẩm...)
    lên server qua endpoint này.

    Args:
        Request Body (JSON):
            - coop_ id (int): ID chuồng (bắt buộc)
            - temperature (float): Nhiệt độ (°C)
            - humidity (float): Độ ẩm (%)
            - feed_ level (float): Mức thức ăn (%)
            - water_level (float): Mức nước (%)
            - recorded_at (str, optional): Thời gian ghi nhận (ISO format)

    Returns:
        201: Environment object đã lưu
        400: Thi���u coop_ id
        404: Không tìm thấy chuồng
    """
    data = request.get_json()
    coop_id = data.get('coop_id')

    if not coop_id:
        return jsonify({'error': 'coop_id required'}), 400

    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404

    recorded_at = data.get('recorded_at')
    if recorded_at:
        try:
            recorded_at = datetime.fromisoformat(recorded_at)
        except ValueError:
            recorded_at = datetime.utcnow()
    else:
        recorded_at = datetime.utcnow()

    from models import db
    env = Environment(
        coop_id=coop_id,
        temperature=data.get('temperature'),
        humidity=data.get('humidity'),
        feed_level=data.get('feed_level'),
        water_level=data.get('water_level'),
        recorded_at=recorded_at
    )
    db.session.add(env)
    db.session.commit()

    return jsonify(env.to_dict()), 201


@environment_bp.route('/<int:coop_id>', methods=['GET'])
@jwt_required()
def get_environment(coop_id):
    """
    Lấy thông số môi trường hiện tại của một chuồng.

    Args:
        coop_id (int): ID chuồng

    Returns:
        200: Environment object mới nhất
        404: Không tìm thấy chuồng hoặc chưa có dữ liệu
    """
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404

    env = Environment.query.filter_by(coop_id=coop_id).order_by(
        Environment.recorded_at.desc()
    ).first()

    if not env:
        return jsonify({'error': 'No environment data'}), 404

    return jsonify(env.to_dict()), 200


@environment_bp.route('/<int:coop_id>/history', methods=['GET'])
@jwt_required()
def get_environment_history(coop_id):
    """
    Lấy dữ liệu lịch sử môi trường để vẽ biểu đồ.

    Args:
        coop_id (int): ID chuồng
        limit (int, query param): Số bản ghi (mặc định: 24)
        from_date (str, query param): Từ ngày (ISO format)
        to_date (str, query param): Đến ngày (ISO format)

    Returns:
        200: Array of Environment objects sắp xếp recorded_at DESC
        404: Không tìm thấy chuồng
    """
    coop = Coop.query.get(coop_id)
    if not coop:
        return jsonify({'error': 'Coop not found'}), 404

    limit = request.args.get('limit', 24, type=int)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    query = Environment.query.filter_by(coop_id=coop_id)

    if from_date:
        try:
            query = query.filter(Environment.recorded_at >= datetime.fromisoformat(from_date))
        except ValueError:
            pass

    if to_date:
        try:
            query = query.filter(Environment.recorded_at <= datetime.fromisoformat(to_date))
        except ValueError:
            pass

    environments = query.order_by(Environment.recorded_at.desc()).limit(limit).all()

    return jsonify([env.to_dict() for env in environments]), 200