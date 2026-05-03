"""
Tests for Coops API endpoints
"""
import json


class TestGetCoops:
    """Test getting list of coops."""
    
    def test_get_coops_success(self, client, admin_headers, test_coop):
        """Test getting all coops."""
        response = client.get('/api/coops', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]['name'] == 'Test Coop'
    
    def test_get_coops_without_auth(self, client):
        """Test getting coops without JWT token."""
        response = client.get('/api/coops')
        
        assert response.status_code == 401


class TestCreateCoop:
    """Test creating a new coop."""
    
    def test_create_coop_success(self, client, admin_headers):
        """Test successful coop creation."""
        response = client.post('/api/coops', headers=admin_headers, json={
            'name': 'New Coop',
            'location': 'New Location',
            'capacity': 800,
            'current_count': 200,
            'area': 80.0,
            'temp_min': 20.0,
            'temp_max': 30.0,
            'humidity_min': 45.0,
            'humidity_max': 75.0
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'New Coop'
        assert data['location'] == 'New Location'
        assert data['capacity'] == 800
        assert data['temp_min'] == 20.0
    
    def test_create_coop_minimal(self, client, admin_headers):
        """Test creating coop with minimal required fields."""
        response = client.post('/api/coops', headers=admin_headers, json={
            'name': 'Minimal Coop'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Minimal Coop'
        assert data['capacity'] == 500  # default
        assert data['auto_fan'] is True  # default


class TestGetCoop:
    """Test getting a specific coop."""
    
    def test_get_coop_success(self, client, admin_headers, test_coop):
        """Test getting a coop by ID."""
        response = client.get(f'/api/coops/{test_coop.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_coop.id
        assert data['name'] == 'Test Coop'
    
    def test_get_coop_not_found(self, client, admin_headers):
        """Test getting non-existent coop."""
        response = client.get('/api/coops/9999', headers=admin_headers)
        
        assert response.status_code == 404


class TestUpdateCoop:
    """Test updating a coop."""
    
    def test_update_coop_success(self, client, admin_headers, test_coop):
        """Test successful coop update."""
        response = client.put(f'/api/coops/{test_coop.id}', headers=admin_headers, json={
            'name': 'Updated Coop',
            'capacity': 1200,
            'temp_min': 15.0
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Coop'
        assert data['capacity'] == 1200
        assert data['temp_min'] == 15.0
        assert data['location'] == 'Test Location'  # unchanged
    
    def test_update_coop_not_found(self, client, admin_headers):
        """Test updating non-existent coop."""
        response = client.put('/api/coops/9999', headers=admin_headers, json={
            'name': 'Updated'
        })
        
        assert response.status_code == 404


class TestDeleteCoop:
    """Test deleting a coop."""
    
    def test_delete_coop_success(self, client, admin_headers, test_coop):
        """Test successful coop deletion."""
        response = client.delete(f'/api/coops/{test_coop.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'deleted' in data.get('message', '').lower()
    
    def test_delete_coop_not_found(self, client, admin_headers):
        """Test deleting non-existent coop."""
        response = client.delete('/api/coops/9999', headers=admin_headers)
        
        assert response.status_code == 404


class TestGetCoopDevices:
    """Test getting devices in a coop."""
    
    def test_get_coop_devices_empty(self, client, admin_headers, test_coop):
        """Test getting devices when coop has none."""
        response = client.get(f'/api/coops/{test_coop.id}/devices', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_coop_devices_not_found(self, client, admin_headers):
        """Test getting devices for non-existent coop."""
        response = client.get('/api/coops/9999/devices', headers=admin_headers)
        
        assert response.status_code == 404


class TestGetCoopEnvironment:
    """Test getting coop environment data."""
    
    def test_get_coop_environment_success(self, client, admin_headers, test_coop, test_environment):
        """Test getting latest environment data."""
        response = client.get(f'/api/coops/{test_coop.id}/environment', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'temperature' in data
        assert 'humidity' in data
        assert data['coop_id'] == test_coop.id
    
    def test_get_coop_environment_no_data(self, client, admin_headers, test_coop):
        """Test getting environment when no data exists."""
        response = client.get(f'/api/coops/{test_coop.id}/environment', headers=admin_headers)
        
        assert response.status_code == 404


class TestGetCoopHistory:
    """Test getting coop environment history."""
    
    def test_get_coop_history(self, client, admin_headers, test_coop, test_environment):
        """Test getting environment history."""
        response = client.get(f'/api/coops/{test_coop.id}/history', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_coop_history_with_limit(self, client, admin_headers, test_coop, test_environment):
        """Test getting history with limit parameter."""
        response = client.get(f'/api/coops/{test_coop.id}/history?limit=5', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
