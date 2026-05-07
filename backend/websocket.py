"""
WebSocket Server - Real-time communication với Socket.io

Xử lý các sự kiện WebSocket:
- Kết nối/ngắt kết nối client
- Gửi cập nhật real-time cho dashboard, coop, devices
- Tự động phát dữ liệu khi có thay đổi từ database
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token, verify_jwt_in_request
from functools import wraps
from datetime import datetime
import logging

# Cấu hình SocketIO với CORS
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',  # Hoặc 'eventlet' nếu đã cài
    logger=True,
    engineio_logger=False
)

# Logger
logger = logging.getLogger(__name__)


# ============================================================
# JWT Authentication Decorator cho WebSocket
# ============================================================

def authenticated_only(f):
    """
    Decorator kiểm tra JWT token trong WebSocket events
    Token được gửi trong query param khi kết nối: ?token=xxx
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        # Lấy token từ args (được gửi qua query string)
        if len(args) > 0 and isinstance(args[0], dict):
            data = args[0]
            token = data.get('token') or data.get('query', {}).get('token')
        else:
            token = None
        
        if not token:
            emit('error', {'message': 'Authentication required'})
            return
        
        try:
            # Verify JWT token
            from flask_jwt_extended import decode_token
            decoded = decode_token(token)
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"JWT verification failed: {e}")
            emit('error', {'message': 'Invalid token'})
            return
    
    return wrapped


# ============================================================
# WebSocket Event Handlers
# ============================================================

@socketio.on('connect')
def handle_connect():
    """
    Xử lý khi client kết nối
    Gửi dữ liệu dashboard ngay lập tức
    """
    logger.info(f"Client connected: {getattr(request, 'sid', 'unknown')}")
    
    # Gửi dữ liệu dashboard ban đầu
    try:
        from models import Coop, Device, Environment, Alert, db
        
        with socketio.server.app.app_context():
            # Tính toán dữ liệu dashboard
            coops = Coop.query.all()
            devices = Device.query.all()
            
            total_coops = len(coops)
            total_devices = len(devices)
            online_devices = len([d for d in devices if d.status == 'online'])
            
            # Tính nhiệt độ/độ ẩm trung bình
            avg_temp = 0
            avg_humid = 0
            if coops:
                for coop in coops:
                    env = Environment.query.filter_by(coop_id=coop.id).order_by(Environment.recorded_at.desc()).first()
                    if env:
                        avg_temp += env.temperature or 0
                        avg_humid += env.humidity or 0
                
                avg_temp /= len(coops)
                avg_humid /= len(coops)
            
            # Trạng thái thiết bị
            device_status_counts = {
                'online': len([d for d in devices if d.status == 'online']),
                'offline': len([d for d in devices if d.status == 'offline']),
                'waiting': len([d for d in devices if d.status == 'connecting'])
            }
            
            # Gửi dữ liệu cho client vừa kết nối
            emit('dashboard:overview', {
                'total_coops': total_coops,
                'total_devices': total_devices,
                'online_devices': online_devices,
                'avg_temperature': round(avg_temp, 1),
                'avg_humidity': round(avg_humid, 1),
                'device_status_counts': device_status_counts,
                'timestamp': datetime.now().isoformat()
            })
            
            # Gửi danh sách chuồng
            coops_data = []
            for coop in coops:
                env = Environment.query.filter_by(coop_id=coop.id).order_by(Environment.recorded_at.desc()).first()
                coops_data.append({
                    'id': coop.id,
                    'name': coop.name,
                    'status': coop.status,
                    'current_count': coop.current_count,
                    'temperature': env.temperature if env else None,
                    'humidity': env.humidity if env else None
                })
            
            emit('coop:status', coops_data)
            
            # Gửi danh sách thiết bị
            devices_data = []
            for device in devices:
                devices_data.append({
                    'id': device.id,
                    'name': device.name,
                    'status': device.status,
                    'type': device.type,
                    'coop_id': device.coop_id if hasattr(device, 'coop_id') else None
                })
            
            emit('device:status', devices_data)
            
    except Exception as e:
        logger.error(f"Error sending initial data: {e}")


@socketio.on('disconnect')
def handle_disconnect():
    """Xử lý khi client ngắt kết nối"""
    logger.info(f"Client disconnected: {getattr(request, 'sid', 'unknown')}")


@socketio.on('subscribe:coop')
def handle_subscribe_coop(data):
    """
    Client đăng ký nhận cập nhật cho một chuồng cụ thể
    data: { coop_id: 1 }
    """
    coop_id = data.get('coop_id')
    if coop_id:
        room = f'coop_{coop_id}'
        join_room(room)
        logger.info(f"Client subscribed to coop {coop_id}")
        
        # Gửi dữ liệu hiện tại của chuồng
        try:
            from models import Coop, Environment
            with socketio.server.app.app_context():
                coop = Coop.query.get(coop_id)
                if coop:
                    env = Environment.query.filter_by(coop_id=coop_id).order_by(Environment.recorded_at.desc()).first()
                    emit('coop:update:' + str(coop_id), {
                        'id': coop.id,
                        'name': coop.name,
                        'status': coop.status,
                        'current_count': coop.current_count,
                        'temperature': env.temperature if env else None,
                        'humidity': env.humidity if env else None
                    })
        except Exception as e:
            logger.error(f"Error fetching coop data: {e}")


@socketio.on('unsubscribe:coop')
def handle_unsubscribe_coop(data):
    """Client hủy đăng ký nhận cập nhật chuồng"""
    coop_id = data.get('coop_id')
    if coop_id:
        room = f'coop_{coop_id}'
        leave_room(room)
        logger.info(f"Client unsubscribed from coop {coop_id}")


# ============================================================
# Utility Functions - Gửi cập nhật từ server
# ============================================================

def broadcast_dashboard_update():
    """
    Gửi cập nhật dashboard tới tất cả clients
    Gọi hàm này khi có thay đổi dữ liệu (từ REST API hoặc sensor)
    """
    try:
        from models import Coop, Device, Environment, db
        
        with socketio.server.app.app_context():
            coops = Coop.query.all()
            devices = Device.query.all()
            
            total_coops = len(coops)
            total_devices = len(devices)
            online_devices = len([d for d in devices if d.status == 'online'])
            
            # Tính nhiệt độ/độ ẩm trung bình
            avg_temp = 0
            avg_humid = 0
            if coops:
                for coop in coops:
                    env = Environment.query.filter_by(coop_id=coop.id).order_by(Environment.recorded_at.desc()).first()
                    if env:
                        avg_temp += env.temperature or 0
                        avg_humid += env.humidity or 0
                
                avg_temp /= len(coops)
                avg_humid /= len(coops)
            
            socketio.emit('dashboard:overview', {
                'total_coops': total_coops,
                'total_devices': total_devices,
                'online_devices': online_devices,
                'avg_temperature': round(avg_temp, 1),
                'avg_humidity': round(avg_humid, 1),
                'timestamp': datetime.now().isoformat()
            }, namespace='/')
            
    except Exception as e:
        logger.error(f"Error broadcasting dashboard update: {e}")


def broadcast_coop_update(coop_id):
    """
    Gửi cập nhật cho một chuồng cụ thể
    Gọi khi có thay đổi: nhiệt độ, độ ẩm, số gà...
    """
    try:
        from models import Coop, Environment
        
        with socketio.server.app.app_context():
            coop = Coop.query.get(coop_id)
            if coop:
                env = Environment.query.filter_by(coop_id=coop_id).order_by(Environment.recorded_at.desc()).first()
                
                data = {
                    'id': coop.id,
                    'name': coop.name,
                    'status': coop.status,
                    'current_count': coop.current_count,
                    'temperature': env.temperature if env else None,
                    'humidity': env.humidity if env else None,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Gửi tới phòng riêng của chuồng
                socketio.emit('coop:update:' + str(coop_id), data, room=f'coop_{coop_id}', namespace='/')
                
                # Gửi cập nhật trạng thái chung
                socketio.emit('coop:status', [data], namespace='/')
                
    except Exception as e:
        logger.error(f"Error broadcasting coop update: {e}")


def broadcast_device_update(device_id):
    """
    Gửi cập nhật trạng thái thiết bị
    Gọi khi device thay đổi status (online/offline/error)
    """
    try:
        from models import Device
        
        with socketio.server.app.app_context():
            device = Device.query.get(device_id)
            if device:
                data = {
                    'id': device.id,
                    'name': device.name,
                    'status': device.status,
                    'type': device.type,
                    'coop_id': device.coop_id if hasattr(device, 'coop_id') else None,
                    'timestamp': datetime.now().isoformat()
                }
                
                socketio.emit('device:update:' + str(device_id), data, namespace='/')
                socketio.emit('device:status', [data], namespace='/')
                
    except Exception as e:
        logger.error(f"Error broadcasting device update: {e}")


def broadcast_environment_update(coop_id, env_data):
    """
    Gửi cập nhật dữ liệu môi trường
    env_data: { temperature: 25.5, humidity: 60.0, ... }
    """
    data = {
        'coop_id': coop_id,
        'temperature': env_data.get('temperature'),
        'humidity': env_data.get('humidity'),
        'light_intensity': env_data.get('light_intensity'),
        'ammonia': env_data.get('ammonia'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Gửi tới phòng chuồng
    socketio.emit('environment:update', data, room=f'coop_{coop_id}', namespace='/')
    
    # Gửi cập nhật dashboard tổng (nếu cần)
    broadcast_dashboard_update()


def broadcast_new_alert(alert_data):
    """
    Gửi cảnh báo mới tới tất cả clients
    """
    socketio.emit('alert:new', alert_data, namespace='/')


def broadcast_coop_deleted(coop_id):
    """
    Thông báo cho tất cả clients biết một chuồng đã bị xóa
    """
    try:
        socketio.emit('coop:deleted', {
            'coop_id': coop_id,
            'timestamp': datetime.now().isoformat()
        }, namespace='/')
    except Exception as e:
        logger.error(f"Error broadcasting coop deletion: {e}")
