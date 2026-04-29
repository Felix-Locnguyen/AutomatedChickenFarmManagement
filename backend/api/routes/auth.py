"""
Auth Routes - API xác thực người dùng

Module này cung cấp các endpoint cho việc:
- Đăng ký tài khoản mới
- Đăng nhập và lấy JWT token
- Lấy thông tin người dùng hiện tại
- Đăng xuất

Cơ chế xác thực:
- Sử dụng JWT (JSON Web Token) cho stateless authentication
- Mật khẩu được hash bằng werkzeug.security (PBKDF2+SHA256)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sys
import os

# Thêm đường dẫn parent vào sys.path để có thể import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import User

# Tạo Blueprint với tên 'auth'
# URL prefix sẽ là /api/auth (được thêm từ api_bp trong __init__.py)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Đăng nhập người dùng.
    
    Xác thực username và password, trả về JWT token nếu thành công.
    
    Args:
        Request Body (JSON):
            - username (str): Tên đăng nhập
            - password (str): Mật khẩu
        
    Returns:
        200: {
            "access_token": "jwt_token_string",
            "user": {
                "id": 1,
                "username": "admin",
                "full_name": "Administrator",
                "role": "admin"
            }
        }
        400: Thiếu username hoặc password
        401: Sai username hoặc password
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Validate input
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Tìm user trong database
    user = User.query.filter_by(username=username).first()
    
    # Verify password (sử dụng check_password_hash để so sánh với hash lưu trong DB)
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Tạo JWT token với user.id làm identity
    access_token = create_access_token(identity=user.id)
    
    # Trả về token và thông tin user
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role
        }
    }), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Đăng ký tài khoản người dùng mới.
    
    Tạo tài khoản mới với username và email unique.
    Mật khẩu được hash trước khi lưu vào database.
    
    Args:
        Request Body (JSON):
            - username (str): Tên đăng nhập (bắt buộc, unique)
            - email (str): Email (bắt buộc, unique)
            - password (str): Mật khẩu (bắt buộc)
            - full_name (str): Họ tên (tùy chọn)
        
    Returns:
        201: {
            "message": "User registered successfully",
            "user_id": 1
        }
        400: Thiếu thông tin bắt buộc hoặc username/email đã tồn tại
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name', '')
    
    # Validate required fields
    if not username or not email or not password:
        return jsonify({'error': 'Username, email, password required'}), 400
    
    # Kiểm tra username đã tồn tại chưa
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # Kiểm tra email đã tồn tại chưa
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Hash password trước khi lưu (bảo mật)
    # sử dụng PBKDF2-SHA256 mặc định của werkzeug
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        full_name=full_name,
        role='user'  # Mặc định là user, có thể nâng cấp lên admin
    )
    
    # Lưu vào database
    from api import db
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201


@auth_bp.route('/me', methods=['GET'])
@jwt_required()  # Decorator yêu cầu JWT token hợp lệ
def get_current_user():
    """
    Lấy thông tin người dùng hiện tại.
    
    Sử dụng JWT token từ header Authorization để xác định user.
    Trả về thông tin profile của user đang đăng nhập.
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        200: {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Administrator",
            "role": "admin",
            "created_at": "2025-01-01T00:00:00"
        }
        401: Token không hợp lệ hoặc hết hạn
        404: User không tồn tại
    """
    # Lấy user_id từ JWT token (đã được giải mã bởi @jwt_required)
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Đăng xuất người dùng.
    
    Với JWT stateless, server không cần làm gì đặc biệt.
    Client cần xóa token khỏi storage.
    (Có thể thêm token vào blacklist để chặn token đã logout)
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        200: {"message": "Logged out successfully"}
        401: Token không hợp lệ
    """
    # Với JWT stateless, logout chỉ cần thông báo thành công
    # Client sẽ tự xóa token
    # Để tăng bảo mật, có thể thêm token vào Redis blacklist
    return jsonify({'message': 'Logged out successfully'}), 200