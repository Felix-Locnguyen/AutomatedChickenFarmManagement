"""
API Blueprint Factory - Tạo và đăng ký các Blueprint cho ứng dụng

Blueprint là một cách để tổ chức và chia nhỏ ứng dụng Flask thành các module riêng biệt.
Mỗi Blueprint định nghĩa một tập hợp các routes, views, và templates riêng.
"""

from flask import Blueprint

# Tạo Blueprint chính với url_prefix='/api'
# Tất cả các route trong các blueprint con sẽ có prefix là /api
# Ví dụ: /api/auth/login, /api/coops, /api/devices
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import các blueprint con từ thư mục routes
# Lưu ý: Import được đặt ở cuối file để tránh circular import
# (Khi các module chưa được khởi tạo hoàn chỉnh)
from api.routes import auth, coops, devices, dashboard, camera