"""
Tests for Alerts API endpoints
"""
import json


class TestGetAlerts:
    """Test getting list of alerts."""
    
    def test_get_alerts_success(self, client, admin_headers, test_alert):
        """Test getting all alerts."""
        response = client.get('/api/alerts', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert 'coop_name' in data[0]
        assert 'device_name' in data[0]
        assert 'device_type' in data[0]
    
    def test_get_alerts_filter_resolved(self, client, admin_headers, test_alert, _db):
        """Test filtering alerts by resolved status."""
        from models import Alert
        # Create resolved alert
        resolved_alert = Alert(
            coop_id=test_alert.coop_id,
            device_id=test_alert.device_id,
            type='humidity',
            level='info',
            message='Resolved alert',
            is_resolved=True
        )
        _db.session.add(resolved_alert)
        _db.session.commit()
        
        # Get only unresolved (is_resolved=false)
        response = client.get('/api/alerts?is_resolved=false', headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        for alert in data:
            assert alert['is_resolved'] is False
        
        # Get only resolved (is_resolved=true)
        response = client.get('/api/alerts?is_resolved=true', headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        for alert in data:
            assert alert['is_resolved'] is True
    
    def test_get_alerts_filter_level(self, client, admin_headers, test_alert):
        """Test filtering alerts by level."""
        response = client.get('/api/alerts?level=warning', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        for alert in data:
            assert alert['level'] == 'warning'
    
    def test_get_alerts_filter_coop(self, client, admin_headers, test_alert):
        """Test filtering alerts by coop_id."""
        response = client.get(f'/api/alerts?coop_id={test_alert.coop_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        for alert in data:
            assert alert['coop_id'] == test_alert.coop_id


class TestResolveAlert:
    """Test resolving an alert."""
    
    def test_resolve_alert_success(self, client, admin_headers, test_alert):
        """Test successfully resolving an alert."""
        assert test_alert.is_resolved is False
        
        response = client.put(f'/api/alerts/{test_alert.id}/resolve', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_resolved'] is True
        assert 'resolved_at' in data
    
    def test_resolve_alert_not_found(self, client, admin_headers):
        """Test resolving non-existent alert."""
        response = client.put('/api/alerts/9999/resolve', headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_resolve_already_resolved(self, client, admin_headers, test_alert):
        """Test resolving already resolved alert."""
        # First resolve
        test_alert.is_resolved = True
        from models import db
        db.session.commit()
        
        response = client.put(f'/api/alerts/{test_alert.id}/resolve', headers=admin_headers)
        
        # Should still return 200 (idempotent)
        assert response.status_code == 200
