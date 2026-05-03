from api.routes.auth import auth_bp
from api.routes.coops import coops_bp
from api.routes.devices import devices_bp
from api.routes.dashboard import dashboard_bp
from api.routes.camera import camera_bp
from api.routes.feed_schedule import feed_schedule_bp
from api.routes.environment import environment_bp
from api.routes.alerts import alerts_bp
from api.routes.pages import pages_bp

__all__ = [
    'auth_bp', 'coops_bp', 'devices_bp', 'dashboard_bp', 
    'camera_bp', 'feed_schedule_bp', 'environment_bp', 
    'alerts_bp', 'pages_bp'
]