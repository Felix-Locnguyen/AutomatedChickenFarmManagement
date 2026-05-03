"""
Tests for Devices API endpoints
"""
import json


class TestGetDevices:
    """Test getting list of devices."""
    
    def test_get_devices_success(self, client, admin_headers, test_device):
        """Test getting all devices."""
        response = client.get('/api/devices', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]['name'] == 'Test Sensor'
    
    def test_get_devices_without_auth(self, client):
        """Test getting devices without JWT token."""
        response = client.get('/api/devices')
        
        assert response.status_code == 401


class TestCreateDevice:
    """Test creating a new device."""
    
    def test_create_device_success(self, client, admin_headers):
        """Test successful device creation."""
        response = client.post('/api/devices', headers=admin_headers, json={
            'name': 'New Sensor',
            'type': 'humidity',
            'mac_address': '11:22:33:44:55:66',
            'status': 'offline',
            'is_active': True,
            'battery': 90
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'New Sensor'
        assert data['type'] == 'humidity'
        assert data['mac_address'] == '11:22:33:44:55:66'
    
    def test_create_device_minimal(self, client, admin_headers):
        """Test creating device with minimal fields."""
        response = client.post('/api/devices', headers=admin_headers, json={
            'name': 'Minimal Device',
            'mac_address': 'AA:BB:CC:DD:EE:11'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Minimal Device'
        assert data['type'] == 'sensor'  # default
        assert data['status'] == 'offline'  # default


class TestGetDevice:
    """Test getting a specific device."""
    
    def test_get_device_success(self, client, admin_headers, test_device):
        """Test getting a device by ID."""
        response = client.get(f'/api/devices/{test_device.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_device.id
        assert data['name'] == 'Test Sensor'
    
    def test_get_device_not_found(self, client, admin_headers):
        """Test getting non-existent device."""
        response = client.get('/api/devices/9999', headers=admin_headers)
        
        assert response.status_code == 404


class TestUpdateDevice:
    """Test updating a device."""
    
    def test_update_device_success(self, client, admin_headers, test_device):
        """Test successful device update."""
        response = client.put(f'/api/devices/{test_device.id}', headers=admin_headers, json={
            'name': 'Updated Sensor',
            'battery': 85,
            'status': 'online'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Sensor'
        assert data['battery'] == 85
        assert data['status'] == 'online'
    
    def test_update_device_not_found(self, client, admin_headers):
        """Test updating non-existent device."""
        response = client.put('/api/devices/9999', headers=admin_headers, json={
            'name': 'Updated'
        })
        
        assert response.status_code == 404


class TestDeleteDevice:
    """Test deleting a device."""
    
    def test_delete_device_success(self, client, admin_headers, test_device):
        """Test successful device deletion."""
        response = client.delete(f'/api/devices/{test_device.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'deleted' in data.get('message', '').lower()
    
    def test_delete_device_not_found(self, client, admin_headers):
        """Test deleting non-existent device."""
        response = client.delete('/api/devices/9999', headers=admin_headers)
        
        assert response.status_code == 404


class TestToggleDevice:
    """Test toggling device on/off."""
    
    def test_toggle_device_success(self, client, admin_headers, test_device):
        """Test toggling device state."""
        original_state = test_device.is_active
        
        response = client.post(f'/api/devices/{test_device.id}/toggle', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_active'] != original_state
        assert 'toggled' in data.get('message', '').lower()
    
    def test_toggle_device_not_found(self, client, admin_headers):
        """Test toggling non-existent device."""
        response = client.post('/api/devices/9999/toggle', headers=admin_headers)
        
        assert response.status_code == 404


class TestConnectDevice:
    """Test connecting a new device."""
    
    def test_connect_new_device(self, client, admin_headers):
        """Test connecting a new device."""
        response = client.post('/api/devices/connect', headers=admin_headers, json={
            'device_id': 'NEW_DEVICE_001'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'connecting'
        assert 'Device connecting' in data.get('message', '')
    
    def test_connect_existing_device(self, client, admin_headers, test_device, _db):
        """Test connecting an existing device."""
        # Set device status to offline so it can be connected
        test_device.status = 'offline'
        _db.session.commit()
        
        response = client.post('/api/devices/connect', headers=admin_headers, json={
            'device_id': test_device.mac_address
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'connecting'
    
    def test_connect_device_missing_id(self, client, admin_headers):
        """Test connecting without device_id."""
        response = client.post('/api/devices/connect', headers=admin_headers, json={})
        
        assert response.status_code == 400


class TestAssignDeviceToCoop:
    """Test assigning device to a coop."""
    
    def test_assign_device_success(self, client, admin_headers, test_device, test_coop):
        """Test successful device assignment."""
        response = client.post(f'/api/devices/{test_device.id}/assign', headers=admin_headers, json={
            'coop_id': test_coop.id
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'assigned' in data.get('message', '').lower()
    
    def test_assign_device_already_assigned(self, client, admin_headers, test_device, test_coop, _db):
        """Test assigning already assigned device."""
        from models import CoopDevice
        assign = CoopDevice(coop_id=test_coop.id, device_id=test_device.id)
        _db.session.add(assign)
        _db.session.commit()
        
        response = client.post(f'/api/devices/{test_device.id}/assign', headers=admin_headers, json={
            'coop_id': test_coop.id
        })
        
        assert response.status_code == 400
    
    def test_assign_device_not_found(self, client, admin_headers, test_coop):
        """Test assigning non-existent device."""
        response = client.post('/api/devices/9999/assign', headers=admin_headers, json={
            'coop_id': test_coop.id
        })
        
        assert response.status_code == 404
    
    def test_assign_coop_not_found(self, client, admin_headers, test_device):
        """Test assigning to non-existent coop."""
        response = client.post(f'/api/devices/{test_device.id}/assign', headers=admin_headers, json={
            'coop_id': 9999
        })
        
        assert response.status_code == 404


class TestUpdateDeviceName:
    """Test updating device name after connection."""
    
    def test_update_name_success(self, client, admin_headers, test_device):
        """Test successful name update."""
        response = client.patch(f'/api/devices/{test_device.id}/name', headers=admin_headers, json={
            'name': 'Connected Sensor'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['device']['name'] == 'Connected Sensor'
        assert data['device']['status'] == 'online'
    
    def test_update_name_missing(self, client, admin_headers, test_device):
        """Test updating without name."""
        response = client.patch(f'/api/devices/{test_device.id}/name', headers=admin_headers, json={})
        
        assert response.status_code == 400
    
    def test_update_name_not_found(self, client, admin_headers):
        """Test updating non-existent device."""
        response = client.patch('/api/devices/9999/name', headers=admin_headers, json={
            'name': 'Test'
        })
        
        assert response.status_code == 404
