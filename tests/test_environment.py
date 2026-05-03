"""
Tests for Environment API endpoints
"""
import json
from datetime import datetime, UTC


class TestCreateEnvironment:
    """Test creating environment data."""
    
    def test_create_environment_success(self, client, admin_headers, test_coop):
        """Test successful environment data creation."""
        response = client.post('/api/environment', headers=admin_headers, json={
            'coop_id': test_coop.id,
            'temperature': 26.5,
            'humidity': 65.0,
            'feed_level': 75.0,
            'water_level': 80.0
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['coop_id'] == test_coop.id
        assert data['temperature'] == 26.5
        assert data['humidity'] == 65.0
    
    def test_create_environment_missing_coop_id(self, client, admin_headers):
        """Test creating without coop_id."""
        response = client.post('/api/environment', headers=admin_headers, json={
            'temperature': 26.5
        })
        
        assert response.status_code == 400
    
    def test_create_environment_invalid_coop(self, client, admin_headers):
        """Test creating with non-existent coop."""
        response = client.post('/api/environment', headers=admin_headers, json={
            'coop_id': 9999,
            'temperature': 26.5
        })
        
        assert response.status_code == 404


class TestGetEnvironment:
    """Test getting current environment data."""
    
    def test_get_environment_success(self, client, admin_headers, test_coop, test_environment):
        """Test getting latest environment data."""
        response = client.get(f'/api/environment/{test_coop.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['coop_id'] == test_coop.id
        assert 'temperature' in data
        assert 'humidity' in data
    
    def test_get_environment_no_data(self, client, admin_headers, test_coop):
        """Test getting environment when no data exists."""
        response = client.get(f'/api/environment/{test_coop.id}', headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_get_environment_not_found(self, client, admin_headers):
        """Test getting environment for non-existent coop."""
        response = client.get('/api/environment/9999', headers=admin_headers)
        
        assert response.status_code == 404


class TestGetEnvironmentHistory:
    """Test getting environment history."""
    
    def test_get_history_success(self, client, admin_headers, test_coop, test_environment):
        """Test getting environment history."""
        response = client.get(f'/api/environment/{test_coop.id}/history', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_history_with_limit(self, client, admin_headers, test_coop, test_environment):
        """Test getting history with limit parameter."""
        response = client.get(f'/api/environment/{test_coop.id}/history?limit=5', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_get_history_with_date_filter(self, client, admin_headers, test_coop, test_environment):
        """Test getting history with date filters."""
        from datetime import datetime, timedelta, UTC
        now = datetime.now(UTC)
        from_date = (now - timedelta(days=1)).isoformat()
        to_date = (now + timedelta(days=1)).isoformat()
        
        response = client.get(
            f'/api/environment/{test_coop.id}/history?from_date={from_date}&to_date={to_date}',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_get_history_not_found(self, client, admin_headers):
        """Test getting history for non-existent coop."""
        response = client.get('/api/environment/9999/history', headers=admin_headers)
        
        assert response.status_code == 404
