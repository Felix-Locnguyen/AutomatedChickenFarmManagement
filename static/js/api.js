/**
 * API Helper - Kết nối Frontend với Backend Flask
 * 
 * Sử dụng: Nhúng vào HTML và sử dụng các object: authAPI, dashboardAPI, coopsAPI, devicesAPI, cameraAPI
 * 
 * Ví dụ:
 *   const token = await authAPI.login('admin', 'admin123');
 *   const coops = await coopsAPI.getAll();
 */

(function() {
    'use strict';

    // ============================================================
    // 1. CẤU HÌNH
    // ============================================================
    
    window.API_BASE_URL = '/api';


    // ============================================================
    // 2. TOKEN MANAGEMENT
    // ============================================================

    /**
     * Lấy JWT token từ localStorage
     * @returns {string|null} Token hoặc null nếu không có
     */
    window.getAuthToken = function() {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        if (token === 'null' || token === 'undefined' || token === '') {
            return null;
        }
        return token;
    };

    /**
     * Lưu JWT token vào localStorage
     * @param {string} token - JWT token
     * @param {boolean} remember - Có nhớ không (localStorage vs sessionStorage)
     */
    window.setAuthToken = function(token, remember = false) {
        if (remember) {
            localStorage.setItem('token', token);
        } else {
            sessionStorage.setItem('token', token);
        }
    };

    /**
     * Xóa JWT token
     */
    window.removeAuthToken = function() {
        localStorage.removeItem('token');
        sessionStorage.removeItem('token');
    };

    /**
     * Kiểm tra đã đăng nhập chưa
     * @returns {boolean}
     */
    window.isAuthenticated = function() {
        return !!window.getAuthToken();
    };


    // ============================================================
    // 3. API WRAPPER VỚI ERROR HANDLING
    // ============================================================

    /**
     * Wrapper cho fetch API
     * Tự động thêm Authorization header và xử lý lỗi
     * 
     * @param {string} endpoint - API endpoint (sau /api/)
     * @param {object} options - Options cho fetch
     * @returns {Promise} - Response hoặc throw error
     */
    window.apiFetch = async function(endpoint, options = {}) {
        const token = window.getAuthToken();
        
        // Default headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Thêm Authorization header nếu có token
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Merge options
        const fetchOptions = {
            ...options,
            headers
        };

        try {
            const response = await fetch(`${window.API_BASE_URL}${endpoint}`, fetchOptions);
            
            // Xử lý 401 (Unauthorized) hoặc 422 (Unprocessable Entity - Token hỏng)
            if (response.status === 401 || response.status === 422) {
                const errorData = await response.json().catch(() => ({}));
                console.error('Auth error:', response.status, errorData);
                window.removeAuthToken();
                // Chuyển về trang login nếu không phải đang ở trang login/register
                if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
                    window.location.href = '/login';
                }
                throw new Error(errorData.message || 'Phiên đăng nhập hết hạn hoặc không hợp lệ');
            }

            // Xử lý các mã lỗi khác
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP Error ${response.status}`);
            }

            // Parse JSON response
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();

        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    };


    // ============================================================
    // 4. AUTH API
    // ============================================================

    window.authAPI = {
        /**
         * Đăng nhập
         * @param {string} username 
         * @param {string} password 
         * @returns {object} { token, user }
         */
        login: async function(username, password) {
            const data = await window.apiFetch('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            
            if (data.access_token) {
                window.setAuthToken(data.access_token, true);
            }
            
            return data;
        },

        /**
         * Đăng ký
         * @param {string} username 
         * @param {string} email 
         * @param {string} password 
         * @returns {object}
         */
        register: async function(username, email, password) {
            return await window.apiFetch('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });
        },

        /**
         * Đăng xuất
         */
        logout: function() {
            window.removeAuthToken();
            window.location.href = '/login';
        },

        /**
         * Lấy thông tin user hiện tại
         * @returns {object}
         */
        getMe: async function() {
            return await window.apiFetch('/auth/me');
        }
    };


    // ============================================================
    // 5. DASHBOARD API
    // ============================================================

    window.dashboardAPI = {
        /**
         * Lấy tổng quan dashboard
         * @returns {object}
         */
        getOverview: async function() {
            return await window.apiFetch('/dashboard');
        },

        /**
         * Lấy thống kê chi tiết
         * @returns {object}
         */
        getStats: async function() {
            return await window.apiFetch('/dashboard/stats');
        },

        /**
         * Lấy danh sách cảnh báo
         * @returns {array}
         */
        getAlerts: async function() {
            return await window.apiFetch('/dashboard/alerts');
        },

        /**
         * Lấy hoạt động gần đây
         * @returns {array}
         */
        getRecentActivities: async function() {
            return await window.apiFetch('/dashboard/recent-activities');
        }
    };


    // ============================================================
    // 6. COOPS API
    // ============================================================

    window.coopsAPI = {
        /**
         * Lấy danh sách tất cả chuồng
         * @returns {array}
         */
        getAll: async function() {
            return await window.apiFetch('/coops');
        },

        /**
         * Lấy thông tin một chuồng
         * @param {number} id - ID của chuồng
         * @returns {object}
         */
        getOne: async function(id) {
            return await window.apiFetch(`/coops/${id}`);
        },

        /**
         * Tạo chuồng mới
         * @param {object} coopData 
         * @returns {object}
         */
        create: async function(coopData) {
            return await window.apiFetch('/coops', {
                method: 'POST',
                body: JSON.stringify(coopData)
            });
        },

        /**
         * Cập nhật chuồng
         * @param {number} id 
         * @param {object} coopData 
         * @returns {object}
         */
        update: async function(id, coopData) {
            return await window.apiFetch(`/coops/${id}`, {
                method: 'PUT',
                body: JSON.stringify(coopData)
            });
        },

        /**
         * Xóa chuồng
         * @param {number} id 
         */
        delete: async function(id) {
            return await window.apiFetch(`/coops/${id}`, {
                method: 'DELETE'
            });
        },

        /**
         * Lấy thiết bị trong chuồng
         * @param {number} id 
         * @returns {array}
         */
        getDevices: async function(id) {
            return await window.apiFetch(`/coops/${id}/devices`);
        },

        /**
         * Lấy dữ liệu môi trường hiện tại
         * @param {number} id 
         * @returns {object}
         */
        getEnvironment: async function(id) {
            return await window.apiFetch(`/coops/${id}/environment`);
        },

        /**
         * Lấy lịch sử dữ liệu môi trường
         * @param {number} id 
         * @param {number} limit 
         * @returns {array}
         */
        getHistory: async function(id, limit = 24) {
            return await window.apiFetch(`/coops/${id}/history?limit=${limit}`);
        }
    };


    // ============================================================
    // 7. DEVICES API
    // ============================================================

    window.devicesAPI = {
        /**
         * Lấy danh sách thiết bị
         * @returns {array}
         */
        getAll: async function() {
            return await window.apiFetch('/devices');
        },

        /**
         * Lấy thông tin một thiết bị
         * @param {number} id 
         * @returns {object}
         */
        getOne: async function(id) {
            return await window.apiFetch(`/devices/${id}`);
        },

        /**
         * Bật/tắt thiết bị
         * @param {number} id 
         * @returns {object}
         */
        toggle: async function(id) {
            return await window.apiFetch(`/devices/${id}/toggle`, {
                method: 'POST'
            });
        },

        /**
         * Gán thiết bị vào chuồng
         * @param {number} id 
         * @param {number} coopId 
         * @returns {object}
         */
        assign: async function(id, coopId) {
            return await window.apiFetch(`/devices/${id}/assign`, {
                method: 'POST',
                body: JSON.stringify({ coop_id: coopId })
            });
        },

        /**
         * Cập nhật tên thiết bị
         * @param {number} id 
         * @param {string} name 
         * @returns {object}
         */
        updateName: async function(id, name) {
            return await window.apiFetch(`/devices/${id}/name`, {
                method: 'PATCH',
                body: JSON.stringify({ name })
            });
        },

        /**
         * Tạo thiết bị mới
         * @param {object} deviceData 
         * @returns {object}
         */
        create: async function(deviceData) {
            return await window.apiFetch('/devices', {
                method: 'POST',
                body: JSON.stringify(deviceData)
            });
        },

        /**
         * Xóa thiết bị
         * @param {number} id 
         */
        delete: async function(id) {
            return await window.apiFetch(`/devices/${id}`, {
                method: 'DELETE'
            });
        }
    };


    // ============================================================
    // 8. CAMERA API
    // ============================================================

    window.cameraAPI = {
        /**
         * Lấy danh sách camera
         * @returns {array}
         */
        getAll: async function() {
            return await window.apiFetch('/camera');
        },

        /**
         * Lấy thông tin một camera
         * @param {number} id 
         * @returns {object}
         */
        getOne: async function(id) {
            return await window.apiFetch(`/camera/${id}`);
        },

        /**
         * Lấy camera theo chuồng
         * @param {number} coopId 
         * @returns {array}
         */
        getByCoop: async function(coopId) {
            return await window.apiFetch(`/camera/coop/${coopId}`);
        }
    };


    // ============================================================
    // 9. ALERTS API
    // ============================================================

    window.alertsAPI = {
        /**
         * Lấy danh sách cảnh báo
         * @param {object} filters - { is_resolved, level, coop_id }
         * @returns {array}
         */
        getAll: async function(filters = {}) {
            const queryString = new URLSearchParams(filters).toString();
            const endpoint = queryString ? `/alerts?${queryString}` : '/alerts';
            return await window.apiFetch(endpoint);
        },

        /**
         * Đánh dấu cảnh báo đã xử lý
         * @param {number} id 
         * @returns {object}
         */
        resolve: async function(id) {
            return await window.apiFetch(`/alerts/${id}/resolve`, {
                method: 'PUT'
            });
        }
    };


    // ============================================================
    // 10. UTILITY FUNCTIONS
    // ============================================================

    /**
     * Kiểm tra và chuyển hướng nếu chưa đăng nhập
     */
    window.requireAuth = function() {
        if (!window.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    };

    /**
     * Hiển thị toast notification
     * @param {string} message 
     * @param {string} type - 'success', 'error', 'warning', 'info'
     */
    window.showToast = function(message, type = 'info') {
        // Tạo toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        
        // Style inline (có thể custom trong CSS)
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            animation: slideIn 0.3s ease;
            background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#3b82f6'};
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove sau 3s
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };

    /**
     * Format ngày giờ
     * @param {string|Date} date 
     * @returns {string}
     */
    window.formatDateTime = function(date) {
        const d = new Date(date);
        return d.toLocaleString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    console.log('✓ api.js loaded - API helper ready');

})();