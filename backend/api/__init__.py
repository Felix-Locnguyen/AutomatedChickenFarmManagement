"""API Blueprint Factory - Tạo và đăng ký các Blueprint cho ứng dụng"""
from flask import Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')
from api. routes import auth, coops, devices, dashboard, camera, feed_schedule, environment