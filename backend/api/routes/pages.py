"""
Pages Blueprint - Định nghĩa các route cho giao diện người dùng (Frontend)

Sử dụng Flask + Jinja2 template engine để render HTML.
Mỗi route tương ứng với một trang trong ứng dụng.

Blueprint này không sử dụng URL prefix (đăng ký ở root level).
"""

from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps


# ============================================================
# 1. KHỞI TẠO BLUEPRINT
# ============================================================

# name='pages': Tên định danh cho blueprint
# import_name='pages': Tên package import
pages_bp = Blueprint('pages', __name__)


# ============================================================
# 2. DECORATOR KIỂM TRA ĐĂNG NHẬP
# ============================================================

def login_required(f):
    """
    Decorator kiểm tra người dùng đã đăng nhập chưa.
    
    Sử dụng:
        @login_required
        def protected_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra session 'user_id' hoặc 'token'
        if 'user_id' not in session and 'token' not in session:
            # Chưa đăng nhập -> chuyển về trang login
            return redirect(url_for('pages.login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# 3. TRANG CHỦ & DASHBOARD
# ============================================================

@pages_bp.route('/')
def index():
    """
    Trang chủ - Dashboard chính
    
    Render template: index.html
    
    Kiểm tra đăng nhập trong frontend (JS)
    """
    return render_template('index.html')


# ============================================================
# 4. QUẢN LÝ CHUỒNG
# ============================================================

@pages_bp.route('/coops')
def coops_list():
    """
    Trang danh sách chuồng
    
    Render template: coop-list.html
    """
    return render_template('coop-list.html')


@pages_bp.route('/coops/<int:coop_id>')
def coop_detail(coop_id):
    """
    Trang chi tiết một chuồng cụ thể
    
    Args:
        coop_id: ID của chuồng cần xem chi tiết
    
    Render template: coop-detail.html
    Pass variables: coop_id (int)
    """
    return render_template('coop-detail.html', coop_id=coop_id)


# ============================================================
# 5. QUẢN LÝ THIẾT BỊ
# ============================================================

@pages_bp.route('/devices')
def devices_list():
    """
    Trang danh sách thiết bị IoT
    
    Render template: device-list.html
    """
    return render_template('device-list.html')


@pages_bp.route('/devices/<int:device_id>')
def device_detail(device_id):
    """
    Trang chi tiết một thiết bị cụ thể
    
    Args:
        device_id: ID của thiết bị cần xem chi tiết
    
    Render template: device-detail.html
    Pass variables: device_id (int)
    """
    return render_template('device-detail.html', device_id=device_id)


# ============================================================
# 6. QUẢN LÝ CAMERA
# ============================================================

@pages_bp.route('/cameras')
def cameras_list():
    """
    Trang danh sách camera
    
    Render template: camera.html
    """
    return render_template('camera.html')


@pages_bp.route('/cameras/<coop>')
def camera_detail(coop):
    """
    Trang xem camera theo chuồng cụ thể
    
    Args:
        coop: Tên/ID của chuồng cần xem camera (ví dụ: 'A', 'B', 'C'...)
    
    Render template: camera-detail.html
    Pass variables: coop (string)
    """
    return render_template('camera-detail.html', coop=coop)


# ============================================================
# 7. TRANG KHÁC
# ============================================================

@pages_bp.route('/other')
def other():
    """
    Trang các cài đặt và chức năng khác
    
    Render template: other.html
    """
    return render_template('other.html')


# ============================================================
# 8. AUTHENTICATION
# ============================================================

@pages_bp.route('/login')
def login():
    """
    Trang đăng nhập
    
    Logic:
    - Nếu người dùng đã có session (đã đăng nhập) -> redirect về trang chủ /
    - Nếu chưa đăng nhập -> hiển thị form login
    
    Kiểm tra session:
    - 'user_id': ID người dùng (nếu dùng session-based auth)
    - 'token': JWT token (nếu dùng JWT)
    """
    # Kiểm tra nếu đã đăng nhập thì redirect về trang chủ
    if session.get('user_id') or session.get('token'):
        return redirect(url_for('pages.index'))
    
    # Chưa đăng nhập -> hiển thị trang login
    return render_template('login.html')


@pages_bp.route('/register')
def register():
    """
    Trang đăng ký tài khoản
    
    Render template: register.html
    
    Logic tương tự login:
    - Nếu đã đăng nhập -> redirect về trang chủ
    """
    # Kiểm tra nếu đã đăng nhập thì redirect về trang chủ
    if session.get('user_id') or session.get('token'):
        return redirect(url_for('pages.index'))
    
    return render_template('register.html')


@pages_bp.route('/logout')
def logout():
    """
    Route xử lý đăng xuất
    
    Xóa session và chuyển về trang login
    """
    # Xóa các session keys
    session.pop('user_id', None)
    session.pop('token', None)
    session.pop('username', None)
    
    # Chuyển về trang login
    return redirect(url_for('pages.login'))


# ============================================================
# 9. ERROR HANDLERS
# ============================================================

@pages_bp.errorhandler(404)
def page_not_found(error):
    """
    Xử lý lỗi 404 - Trang không tồn tại
    """
    return render_template('404.html'), 404


@pages_bp.errorhandler(500)
def internal_error(error):
    """
    Xử lý lỗi 500 - Lỗi server nội bộ
    """
    return render_template('blank.html'), 500