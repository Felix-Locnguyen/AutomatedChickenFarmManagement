"""
Tests for Auth API endpoints
"""
import json


class TestRegister:
    """Test user registration endpoint."""
    
    def test_register_success(self, client, _db):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'full_name': 'New User'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'user_id' in data
        assert data['message'] == 'Đăng ký thành công'
    
    def test_register_duplicate_username(self, client, admin_user):
        """Test registration with existing username."""
        response = client.post('/api/auth/register', json={
            'username': 'admin_test',
            'email': 'different@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Username' in data.get('error', '')
    
    def test_register_duplicate_email(self, client, admin_user):
        """Test registration with existing email."""
        response = client.post('/api/auth/register', json={
            'username': 'different_user',
            'email': 'admin@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Email' in data.get('error', '')
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post('/api/auth/register', json={
            'username': 'test'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Vui lòng' in data.get('error', '')


class TestLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client, admin_user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'username': 'admin_test',
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'admin_test'
        assert data['user']['role'] == 'admin'
    
    def test_login_wrong_password(self, client, admin_user):
        """Test login with wrong password."""
        response = client.post('/api/auth/login', json={
            'username': 'admin_test',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'không đúng' in data.get('error', '')
    
    def test_login_nonexistent_user(self, client, _db):
        """Test login with non-existent username."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'không đúng' in data.get('error', '')
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post('/api/auth/login', json={
            'username': 'admin_test'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Vui lòng' in data.get('error', '')


class TestLogout:
    """Test user logout endpoint."""
    
    def test_logout_success(self, client, admin_headers):
        """Test successful logout."""
        response = client.post('/api/auth/logout', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'thành công' in data.get('message', '')
    
    def test_logout_without_token(self, client):
        """Test logout without JWT token."""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 401


class TestGetCurrentUser:
    """Test get current user endpoint."""
    
    def test_get_current_user_success(self, client, admin_headers, admin_user):
        """Test getting current user info."""
        response = client.get('/api/auth/me', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'admin_test'
        assert data['email'] == 'admin@test.com'
        assert 'password_hash' not in data
    
    def test_get_current_user_invalid_token(self, client):
        """Test with invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/auth/me', headers=headers)
        
        # JWT may return 401 or 422 for invalid tokens
        assert response.status_code in [401, 422]
    
    def test_get_current_user_no_token(self, client):
        """Test without token."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
