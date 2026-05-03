"""
Pytest Configuration and Fixtures
"""
import sys
import os
import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from models import db, User, Coop, Device, Environment, Alert, CoopDevice, FeedSchedule


@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Cleanup
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def _db(app):
    """Create a fresh database for each test."""
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def admin_user(_db):
    """Create an admin user for testing."""
    user = User(
        username='admin_test',
        email='admin@test.com',
        full_name='Admin Test',
        role='admin'
    )
    user.set_password('admin123')
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture(scope='function')
def worker_user(_db):
    """Create a worker user for testing."""
    user = User(
        username='worker_test',
        email='worker@test.com',
        full_name='Worker Test',
        role='worker'
    )
    user.set_password('worker123')
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture(scope='function')
def admin_headers(app, admin_user):
    """Generate JWT headers for admin user."""
    with app.app_context():
        token = create_access_token(identity=str(admin_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def worker_headers(app, worker_user):
    """Generate JWT headers for worker user."""
    with app.app_context():
        token = create_access_token(identity=str(worker_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def test_coop(_db):
    """Create a test coop."""
    coop = Coop(
        name='Test Coop',
        location='Test Location',
        capacity=500,
        current_count=100,
        area=50.0,
        temp_min=18.0,
        temp_max=28.0,
        humidity_min=40.0,
        humidity_max=70.0
    )
    _db.session.add(coop)
    _db.session.commit()
    return coop


@pytest.fixture(scope='function')
def test_device(_db):
    """Create a test device."""
    device = Device(
        name='Test Sensor',
        type='temperature',
        mac_address='00:11:22:33:44:55',
        status='online',
        is_active=True,
        battery=100
    )
    _db.session.add(device)
    _db.session.commit()
    return device


@pytest.fixture(scope='function')
def test_environment(_db, test_coop):
    """Create test environment data."""
    env = Environment(
        coop_id=test_coop.id,
        temperature=25.0,
        humidity=60.0,
        feed_level=80.0,
        water_level=75.0
    )
    _db.session.add(env)
    _db.session.commit()
    return env


@pytest.fixture(scope='function')
def test_alert(_db, test_coop, test_device):
    """Create a test alert."""
    alert = Alert(
        coop_id=test_coop.id,
        device_id=test_device.id,
        type='temperature',
        level='warning',
        message='Temperature too high',
        is_resolved=False
    )
    _db.session.add(alert)
    _db.session.commit()
    return alert
