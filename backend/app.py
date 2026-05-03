"""
Flask Application Entry Point

Sử dụng mô hình Application Factory (create_app).
Hỗ trợ cấu hình đa môi trường (Development/Production/Testing).
"""

# ============================================================
# 1. IMPORTS - Thư viện cần thiết
# ============================================================

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Import cấu hình và database từ project
from config import config
from models import db

# Import pages blueprint cho frontend routing
from api.routes.pages import pages_bp

# Load biến môi trường từ .env file (nếu có)
load_dotenv()


# ============================================================
# 2. APPLICATION FACTORY FUNCTION
# ============================================================

def create_app(config_name='development'):
    """
    Tạo và cấu hình Flask application.
    
    Args:
        config_name: Tên cấu hình ('development', 'production', 'testing')
                     Mặc định là 'development'
    
    Returns:
        Flask application instance
    """
    
    # --- Khởi tạo Flask app ---
    # template_folder='templates': Chỉ định thư mục chứa HTML templates
    # static_folder: Chỉ định thư mục chứa file tĩnh (CSS, JS, images)
    # Đường dẫn: từ backend/ đi ra ngoài đến static/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    static_dir = os.path.join(project_root, 'static')

    app = Flask(__name__, 
                template_folder=static_dir,
                static_folder=static_dir,
                static_url_path='')
    
    # --- Cấu hình từ config.py ---
    # config[config_name] sẽ lấy class Config tương ứng
    app.config.from_object(config[config_name])
    
    # ============================================================
    # 3. KHỞI TẠO CÁC EXTENSIONS
    # ============================================================
    
    # --- SQLAlchemy Database ---
    # Khởi tạo SQLAlchemy với app
    db.init_app(app)
    
    # --- CORS (Cross-Origin Resource Sharing) ---
    # Cho phép frontend (static folder) gọi API
    # resources={r"/api/*": {"origins": "*"}} chỉ áp dụng cho /api/*
    CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Authorization", "Content-Type"]}})
    
    # --- JWT Manager ---
    # Quản lý xác thực người dùng bằng JWT token
    jwt = JWTManager(app)
    
    # ============================================================
    # 4. REGISTER BLUEPRINTS - Đăng ký API routes
    # ============================================================
    
    # Import api blueprint từ api/__init__.py
    # api_bp đã được định nghĩa với url_prefix='/api'
    from api import api_bp
    app.register_blueprint(api_bp)
    
    # --- Pages Blueprint (Frontend Routes) ---
    # Đăng ký pages_bp KHÔNG có prefix để render HTML trực tiếp
    # Các routes: /, /coops, /devices, /cameras, /login, etc.
    app.register_blueprint(pages_bp)
    
    # ============================================================
    # 5. TẠO DATABASE TỰ ĐỘNG
    # ============================================================
    
    # Tạo các bảng database trong application context
    # db.create_all() sẽ tạo tất cả tables định nghĩa trong models.py
    # Chỉ tạo khi file database chưa tồn tại để tránh ghi đè dữ liệu
    
    with app.app_context():
        # Kiểm tra database đã tồn tại chưa
        db_file = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_file):
            # File database chưa tồn tại -> Tạo mới
            print(f"Creating new database: {db_file}")
            db.create_all()
            print("Database tables created successfully!")
        else:
            # File đã tồn tại -> Chỉ đảm bảo tables tồn tại
            db.create_all()
            print(f"Database already exists: {db_file}")
    
    # ============================================================
    # 6. API HEALTH CHECK ROUTE
    # ============================================================
    
    @app.route('/health')
    def health():
        """
        Health check endpoint
        
        Returns:
            JSON: Trạng thái health của server
        """
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        })
    
    # ============================================================
    # 7. ERROR HANDLERS - Xử lý lỗi
    # ============================================================
    
    @app.errorhandler(404)
    def not_found(error):
        """Xử lý lỗi 404 - Not Found"""
        return jsonify({
            'error': 'Not Found',
            'message': 'Endpoint không tồn tại'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Xử lý lỗi 500 - Internal Server Error"""
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Đã xảy ra lỗi server'
        }), 500
    
    return app


# ============================================================
# 8. MAIN - Chạy ứng dụng
# ============================================================

if __name__ == '__main__':
    """
    Chạy Flask application khi file được execute trực tiếp.
    
    Thiết lập:
        - Host: 0.0.0.0 (cho phép truy cập từ mạng LAN)
        - Port: 5000 (port mặc định của Flask)
        - Debug: True (hiển thị lỗi chi tiết trong development)
    """
    
    # Lấy config từ biến môi trường, mặc định là 'development'
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    print(f"Starting Flask app with config: {config_name}")
    
    # Tạo app và chạy
    app = create_app(config_name)
    
    # Chạy server
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5000,        # Default Flask port
        debug=True       # Enable debug mode
    )