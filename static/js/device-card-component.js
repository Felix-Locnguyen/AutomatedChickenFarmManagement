/**
 * Device Card Component - Component dùng chung cho hiển thị card thiết bị gần đây
 *
 * Sử dụng:
 *   - Import vào HTML: <script src="js/device-card-component.js"></script>
 *   - Render một card: DeviceCardComponent.render(device)
 *   - Render nhiều cards: DeviceCardComponent.renderAll(devices)
 *
 * Mapping status:
 *   - online/connected → online (màu xanh)
 *   - connecting/pending → waiting (màu vàng)
 *   - offline/disconnected/error → offline (màu đỏ)
 */

(function() {
    'use strict';

    window.DeviceCardComponent = {
        /**
         * Tạo HTML cho một card thiết bị
         * @param {Object} device - Dữ liệu thiết bị từ API
         * @returns {string} HTML string
         */
        render: function(device) {
            if (!device) return '';

            // Mapping status
            const status = device.status || 'offline';
            let statusClass, statusText;

            if (status === 'online' || status === 'connected') {
                statusClass = 'online';
                statusText = 'Hoạt động';
            } else if (status === 'connecting' || status === 'pending') {
                statusClass = 'waiting';
                statusText = 'Đang chờ';
            } else {
                statusClass = 'offline';
                statusText = 'Ngắt kết nối';
            }

            const coopName = device.coop_name || 'Chưa lắp đặt';

            return `
                <div class="device-recent-card ${statusClass}">
                    <div class="device-recent-header">
                        <span class="device-recent-name">${device.device_name || 'Thiết bị ' + device.id}</span>
                        <span class="device-recent-coop">${coopName}</span>
                    </div>
                    <div class="device-recent-status">
                        <span class="status-dot ${statusClass}"></span>
                        <span class="status-text ${statusClass}">${statusText}</span>
                    </div>
                </div>
            `;
        },

        /**
         * Render nhiều card thiết bị
         * @param {Array} devices - Mảng dữ liệu thiết bị
         * @returns {string} HTML string
         */
        renderAll: function(devices) {
            if (!Array.isArray(devices) || devices.length === 0) {
                return '<div class="text-muted p-3">Không có thiết bị</div>';
            }
            return devices.map(device => this.render(device)).join('');
        },

        /**
         * Load dữ liệu từ API và render
         * @param {string} containerId - ID của container
         * @param {number} limit - Số lượng thiết bị hiển thị
         */
        loadAndRender: function(containerId, limit) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const apiUrl = '/api/devices/public/recent';
            const token = localStorage.getItem('token') || sessionStorage.getItem('token');

            fetch(apiUrl, {
                headers: token ? { 'Authorization': 'Bearer ' + token } : {}
            })
            .then(function(response) { return response.json(); })
            .then(function(devices) {
                if (!Array.isArray(devices) || devices.length === 0) {
                    container.innerHTML = '<div class="text-muted p-3">Không có thiết bị</div>';
                    return;
                }

                const displayDevices = limit ? devices.slice(0, limit) : devices;
                container.innerHTML = DeviceCardComponent.renderAll(displayDevices);
            })
            .catch(function(error) {
                console.error('Error loading recent devices:', error);
                container.innerHTML = '<div class="text-danger p-3">Không thể tải dữ liệu</div>';
            });
        },

        /**
         * Load dữ liệu với auto-refresh
         * @param {string} containerId - ID của container
         * @param {number} limit - Số lượng thiết bị hiển thị
         * @param {number} interval - Thời gian refresh (ms)
         */
        loadAndRenderWithAutoRefresh: function(containerId, limit, interval) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const self = this;
            const loadData = function() {
                const apiUrl = '/api/devices/public/recent';
                const token = localStorage.getItem('token') || sessionStorage.getItem('token');

                fetch(apiUrl, {
                    headers: token ? { 'Authorization': 'Bearer ' + token } : {}
                })
                .then(function(response) { return response.json(); })
                .then(function(devices) {
                    if (!Array.isArray(devices) || devices.length === 0) {
                        container.innerHTML = '<div class="text-muted p-3">Không có thiết bị</div>';
                        return;
                    }

                    const displayDevices = limit ? devices.slice(0, limit) : devices;
                    container.innerHTML = DeviceCardComponent.renderAll(displayDevices);
                })
                .catch(function(error) {
                    console.error('Error loading recent devices:', error);
                });
            };

            // Load lần đầu
            loadData();

            // Auto-refresh
            if (interval) {
                setInterval(loadData, interval);
            }
        }
    };

    console.log('✓ device-card-component.js loaded - DeviceCardComponent ready');
})();