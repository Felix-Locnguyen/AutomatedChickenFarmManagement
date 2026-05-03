"""
Auth Routes - API Xác thực Người dùng

Module này cung cấp các endpoint cho hệ thống xác thực người dùng:
- POST /api/auth/login: Đăng nhập, nhận JWT token
- POST /api/auth/register: Đăng ký tài khoản mới
- POST /api/auth/logout: Đăng xuất
- GET /api/auth/me: Lấy thông tin user hiện tại

Cơ chế bảo mật:
- JWT (JSON Web Token) cho xác thực stateless
- Werkzeug security cho hash/băm mật khẩu (PBKDF2+SHA256)
- Flask-JWT-Extended để quản lý token
"""

# =============================================================================
# IMPORT THƯ VIỆN
# =============================================================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,  # Tạo JWT token mới
    jwt_required,        # Decorator yêu cầu JWT hợp lệ
    get_jwt_identity    # Lấy user ID từ JWT token
)
from werkzeug.security import (
    generate_password_hash,  # Băm mật khẩu (mã hóa một chiều)
    check_password_hash     # Kiểm tra mật khẩu với hash
)
from datetime import datetime
import sys
import os

# Thêm đường dẫn parent vào sys.path để import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import User, db

# =============================================================================
# TẠO BLUEPRINT
# =============================================================================

auth_bp = Blueprint('auth', __name__)

# =============================================================================
# ENDPOINT 1: ĐĂNG NHẬP (LOGIN)
# =============================================================================

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Đăng nhập người dùng.

    Luồng xử lý:
    1. Nhận username và password từ request body
    2. Validate dữ liệu đầu vào (không được rỗng)
    3. Tìm user trong database theo username
    4. Kiểm tra mật khẩu với hash lưu trong DB
    5. Nếu thành công, tạo JWT token và trả về cho client

    Request Body (JSON):
        {
            "username": "admin",       // Tên đăng nhập (bắt buộc)
            "password": "admin123"     // Mật khẩu (bắt buộc)
        }

    Response thành công (200):
        {
            "access_token": "eyJ0eHAiOiJKV1Q...",  // JWT token
            "user": {
                "id": 1,
                "username": "admin",
                "full_name": "Quản trị viên",
                "role": "admin"
            }
        }

    Response lỗi (400): Thiếu username hoặc password
    Response lỗi (401): Sai username hoặc password
    """
    # Bước 1: Lấy dữ liệu từ request body (JSON)
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Bước 2: Validate - kiểm tra dữ liệu không được rỗng
    if not username or not password:
        return jsonify({
            'error': 'Vui lòng nhập username và password'
        }), 400

    # Bước 3: Tìm user trong database theo username
    user = User.query.filter_by(username=username).first()

    # Bước 4: Kiểm tra mật khẩu
    # check_password_hash() giải mã hash trong DB và so sánh với password gửi lên
    # Nếu sai: trả lỗi 401
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({
            'error': 'Username hoặc password không đúng'
        }), 401

    # Bước 5: Tạo JWT token với user.id làm identity (định danh)
    # Identity được lưu trong token để sau này trích xuất user từ DB
    # Chuyển đổi sang string vì Flask-JWT-Extended yêu cầu identity là string
    access_token = create_access_token(identity=str(user.id))

    # Bước 6: Trả về token và thông tin user (không bao gồm password)
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role
        }
    }), 200

# =============================================================================
# ENDPOINT 2: ĐĂNG KÝ (REGISTER)
# =============================================================================

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Đăng ký tài khoản người dùng mới.

    Luồng xử lý:
    1. Nhận thông tin từ request body
    2. Validate các trường bắt buộc (username, email, password)
    3. Kiểm tra username đã tồn tại chưa
    4. Kiểm tra email đã tồn tại chưa
    5. Hash mật khẩu trước khi lưu vào DB
    6. Tạo user mới và lưu vào database

    Request Body (JSON):
        {
            "username": "user1",          // Tên đăng nhập (bắt buộc, unique)
            "email": "user1@farm.com",    // Email (bắt buộc, unique)
            "password": "pass123",         // Mật khẩu (bắt buộc)
            "full_name": "Nguyễn Văn A"   // Họ tên (tùy chọn)
        }

    Response thành công (201):
        {
            "message": "Đăng ký thành công",
            "user_id": 2
        }

    Response lỗi (400):
        - Thiếu thông tin bắt buộc
        - Username đã tồn tại
        - Email đã tồn tại
    """
    # Bước 1: Lấy dữ liệu từ request body
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name', '')  # Mặc định rỗng nếu không có

    # Bước 2: Validate các trường bắt buộc
    if not username or not email or not password:
        return jsonify({
            'error': 'Vui lòng nhập đầy đủ username, email và password'
        }), 400

    # Bước 3: Kiểm tra username đã tồn tại chưa
    if User.query.filter_by(username=username).first():
        return jsonify({
            'error': 'Username đã được sử dụng'
        }), 400

    # Bước 4: Kiểm tra email đã tồn tại chưa
    if User.query.filter_by(email=email).first():
        return jsonify({
            'error': 'Email đã được sử dụng'
        }), 400

    # Bước 5: Hash mật khẩu trước khi lưu
    # generate_password_hash() sử dụng thuật toán PBKDF2-SHA256
    # Đây là phương pháp mã hóa một chiều, không thể giải mã ngược
    password_hash = generate_password_hash(password)

    # Bước 6: Tạo user mới
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role='worker'  # Mặc định là worker, admin set thủ công
    )

    # Bước 7: Lưu vào database
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Đăng ký thành công',
        'user_id': user.id
    }), 201

# =============================================================================
# ENDPOINT 3: ĐĂNG XUẤT (LOGOUT)
# =============================================================================

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Đăng xuất người dùng.

    Luồng xử lý:
    1. Yêu cầu JWT token hợp lệ từ header
    2. Thông báo đăng xuất thành công
    3. Client tự xóa token khỏi local storage

    Ghi chú về JWT Stateless:
    - JWT là stateless: server không lưu trạng thái session
    - Khi logout, server chỉ cần thông báo thành công
    - Client có trách nhiệm xóa token
    - Token vẫn còn hạn sử dụng cho đến khi hết hạn

    Nâng cao bảo mật (Optional):
    - Có thể lưu token vào Redis blacklist
    - Kiểm tra token trong blacklist trước khi xử lý request
    - Phù hợp cho ứng dụng cần logout thực sự vô hiệu hóa token

    Headers: Authorization: Bearer <jwt_token>

    Response thành công (200):
        {
            "message": "Đăng xuất thành công"
        }

    Response lỗi (401): Token không hợp lệ hoặc hết hạn
    """
    # JWT hợp lệ, thông báo đăng xuất thành công
    return jsonify({
        'message': 'Đăng xuất thành công'
    }), 200

# =============================================================================
# ENDPOINT 4: LẤY THÔNG TIN USER HIỆN TẠI (ME)
# =============================================================================

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Lấy thông tin người dùng hiện tại.

    Luồng xử lý:
    1. Yêu cầu JWT token hợp lệ từ header
    2. Trích xuất user_id từ JWT token
    3. Truy vấn user từ database
    4. Trả về thông tin user (dạng JSON)

    Headers: Authorization: Bearer <jwt_token>

    Response thành công (200):
        {
            "id": 1,
            "username": "admin",
            "email": "admin@chickenfarm.com",
            "full_name": "Quản trị viên",
            "role": "admin",
            "created_at": "2026-04-29T10:00:00"
        }

    Response lỗi (401): Token không hợp lệ hoặc hết hạn
    Response lỗi (404): User không tồn tại (đã bị xóa)
    """
    # Bước 1: Trích xuất user_id từ JWT token
    # get_jwt_identity() trả về giá trị đã truyền vào create_access_token()
    user_id = get_jwt_identity()

    # Bước 2: Truy vấn user từ database theo ID
    user = User.query.get(user_id)

    # Bước 3: Kiểm tra user có tồn tại không
    if not user:
        return jsonify({
            'error': 'Người dùng không tồn tại'
        }), 404

    # Bước 4: Trả về thông tin user (JSON)
    # Không bao gồm password_hash vì lý do bảo mật
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }), 200