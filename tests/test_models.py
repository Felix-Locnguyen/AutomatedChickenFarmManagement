"""
Unit tests for database models
"""
import pytest
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class TestUser:
    """Test User model."""
    
    def test_create_user(self, _db):
        """Test creating a new user."""
        from models import User
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User',
            role='worker'
        )
        user.set_password('password123')
        _db.session.add(user)
        _db.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'worker'
    
    def test_user_password_hash(self, _db):
        """Test password hashing and checking."""
        from models import User
        user = User(username='test2', email='test2@example.com')
        user.set_password('mypassword')
        
        assert user.password_hash is not None
        assert user.password_hash != 'mypassword'
        assert user.check_password('mypassword') is True
        assert user.check_password('wrongpassword') is False
    
    def test_user_to_dict(self, admin_user):
        """Test user to_dict method."""
        user_dict = admin_user.to_dict()
        
        assert 'id' in user_dict
        assert 'username' in user_dict
        assert 'email' in user_dict
        assert 'full_name' in user_dict
        assert 'role' in user_dict
        assert 'password_hash' not in user_dict
        assert user_dict['username'] == admin_user.username


class TestCoop:
    """Test Coop model."""
    
    def test_create_coop(self, _db):
        """Test creating a new coop."""
        from models import Coop
        coop = Coop(
            name='Chuong A',
            location='Khu A',
            capacity=1000,
            current_count=200,
            area=100.0
        )
        _db.session.add(coop)
        _db.session.commit()
        
        assert coop.id is not None
        assert coop.name == 'Chuong A'
        assert coop.capacity == 1000
        assert coop.temp_min == 18.0  # default
        assert coop.auto_fan is True  # default
    
    def test_coop_to_dict(self, test_coop):
        """Test coop to_dict method."""
        coop_dict = test_coop.to_dict()
        
        assert 'id' in coop_dict
        assert 'name' in coop_dict
        assert 'location' in coop_dict
        assert 'capacity' in coop_dict
        assert 'temp_min' in coop_dict
        assert 'temp_max' in coop_dict
        assert coop_dict['name'] == 'Test Coop'


class TestDevice:
    """Test Device model."""
    
    def test_create_device(self, _db):
        """Test creating a new device."""
        from models import Device
        device = Device(
            name='Temperature Sensor',
            type='temperature',
            mac_address='AA:BB:CC:DD:EE:FF',
            status='online',
            is_active=True,
            battery=95
        )
        _db.session.add(device)
        _db.session.commit()
        
        assert device.id is not None
        assert device.type == 'temperature'
        assert device.mac_address == 'AA:BB:CC:DD:EE:FF'
        assert device.battery == 95
    
    def test_device_to_dict(self, test_device):
        """Test device to_dict method."""
        device_dict = test_device.to_dict()
        
        assert 'id' in device_dict
        assert 'name' in device_dict
        assert 'type' in device_dict
        assert 'mac_address' in device_dict
        assert 'status' in device_dict
        assert 'is_active' in device_dict
        assert device_dict['type'] == 'temperature'


class TestEnvironment:
    """Test Environment model."""
    
    def test_create_environment(self, _db, test_coop):
        """Test creating environment record."""
        from models import Environment
        env = Environment(
            coop_id=test_coop.id,
            temperature=26.5,
            humidity=65.0,
            feed_level=70.0,
            water_level=80.0
        )
        _db.session.add(env)
        _db.session.commit()
        
        assert env.id is not None
        assert env.temperature == 26.5
        assert env.coop_id == test_coop.id
    
    def test_environment_to_dict(self, test_environment):
        """Test environment to_dict method."""
        env_dict = test_environment.to_dict()
        
        assert 'id' in env_dict
        assert 'coop_id' in env_dict
        assert 'temperature' in env_dict
        assert 'humidity' in env_dict
        assert env_dict['temperature'] == 25.0


class TestAlert:
    """Test Alert model."""
    
    def test_create_alert(self, _db, test_coop, test_device):
        """Test creating an alert."""
        from models import Alert
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
        
        assert alert.id is not None
        assert alert.level == 'warning'
        assert alert.is_resolved is False
    
    def test_alert_to_dict(self, test_alert):
        """Test alert to_dict method."""
        alert_dict = test_alert.to_dict()
        
        assert 'id' in alert_dict
        assert 'type' in alert_dict
        assert 'level' in alert_dict
        assert 'message' in alert_dict
        assert 'is_resolved' in alert_dict
        assert alert_dict['level'] == 'warning'


class TestFeedSchedule:
    """Test FeedSchedule model."""
    
    def test_create_feed_schedule(self, _db, test_coop):
        """Test creating a feed schedule."""
        from models import FeedSchedule
        from datetime import time
        schedule = FeedSchedule(
            coop_id=test_coop.id,
            time=time(6, 0),
            amount=10.0,
            enabled=True
        )
        _db.session.add(schedule)
        _db.session.commit()
        
        assert schedule.id is not None
        assert schedule.amount == 10.0
        assert schedule.enabled is True
    
    def test_feed_schedule_to_dict(self, _db, test_coop):
        """Test feed schedule to_dict method."""
        from models import FeedSchedule
        from datetime import time
        schedule = FeedSchedule(
            coop_id=test_coop.id,
            time=time(12, 0),
            amount=15.0
        )
        _db.session.add(schedule)
        _db.session.commit()
        
        schedule_dict = schedule.to_dict()
        assert 'id' in schedule_dict
        assert 'coop_id' in schedule_dict
        assert 'time' in schedule_dict
        assert 'amount' in schedule_dict
