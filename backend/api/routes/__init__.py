"""
Routes Package - Xuất các Blueprint từ các module con

Module này đóng vai trò central export point cho tất cả các blueprint trong ứng dụng.
Giúp cho việc import các blueprint từ một nguồn duy nhất thay vì phải import từ nhiều file riêng lẻ.
"""

# Import các blueprint từ từng module con
# Mỗi module chịu trách nhiệm cho một nhóm chức năng riêng biệt

from api.routes.auth import auth_bp      # Auth: login, register, logout, me
from api.routes.coops import coops_bp    # Coops: CRUD chuồng, device management
from api.routes.devices import devices_bp  # Devices: CRUD thiết bị, kết nối
from api.routes.dashboard import dashboard_bp  # Dashboard: thống kê, alerts
from api.routes.camera import camera_bp    # Camera: quản lý camera

# Danh sách các blueprint được export từ package này
# Sử dụng trong app.py để đăng ký các blueprint với Flask app
__all__ = ['auth_bp', 'coops_bp', 'devices_bp', 'dashboard_bp', 'camera_bp']