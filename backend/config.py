"""
Cấu hình ứng dụng Flask

File này định nghĩa các class cấu hình cho different environments:
- Development: Cho local development
- Production: Cho production server
- Testing: Cho unit testing

Các biến cấu hình có thể được override bằng environment variables.
"""

import os
from datetime import timedelta


class Config:
    """
    Cấu hình cơ bản (Base Configuration)
    
    Các thiết lập mặc định cho ứng dụng.
    Được thừa kế bởi các config class khác.
    """
    
    # SECRET_KEY: Dùng cho session signing và các cryptographic operations
    # Lấy từ env hoặc dùng default (nên đổi trong production)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # JWT_SECRET_KEY: Dùng cho JWT token signing
    # Rất quan trọng - nên đặt giá trị phức tạp và giữ bí mật
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key-change-in-production'
    
    # JWT_ACCESS_TOKEN_EXPIRES: Thời hạn của JWT token
    # Mặc định: 24 giờ
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Database Configuration
    # SQLALCHEMY_DATABASE_URI: Chuỗi kết nối database
    # Mặc định dùng SQLite trong thư mục hiện tại
    # Các format khác:
    #   - MySQL: mysql://username:password@localhost/dbname
    #   - PostgreSQL: postgresql://username:password@localhost/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chicken_farm.db'
    
    # SQLALCHEMY_TRACK_MODIFICATIONS: Tắt warning về modifications
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Configuration
    # MAX_CONTENT_LENGTH: Kích thước file tối đa khi upload (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # UPLOAD_FOLDER: Thư mục lưu file upload
    # Mặc định: thư mục 'uploads' trong thư mục backend
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'uploads')


class DevelopmentConfig(Config):
    """
    Cấu hình Development
    
    Sử dụng khi phát triển locally.
    - DEBUG = True: Hiển thị lỗi chi tiết
    - SQLALCHEMY_ECHO = True: In ra SQL queries (hữu ích để debug)
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Cấu hình Production
    
    Sử dụng khi deploy lên server.
    - DEBUG = False: Không hiển thị lỗi chi tiết cho user
    - SQLALCHEMY_ECHO = False: Không in SQL queries (tăng performance)
    """
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Ghi đè SECRET_KEY bắt buộc phải set từ env trong production
    @property
    def SECRET_KEY(cls):
        return os.environ.get('SECRET_KEY') or raise Error("SECRET_KEY must be set in production")


class TestingConfig(Config):
    """
    Cấu hình Testing
    
    Sử dụng khi chạy unit tests.
    - TESTING = True: Bật Flask testing mode
    - SQLALCHEMY_DATABASE_URI = ':memory:': Dùng in-memory SQLite (nhanh, không lưu)
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Config dictionary để dễ dàng access
# Sử dụng: app.config.from_object(config['development'])
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def raise_error(message):
    """Helper function để raise error"""
    raise ValueError(message)