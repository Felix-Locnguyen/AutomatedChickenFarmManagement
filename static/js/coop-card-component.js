/**
 * Coop Card Component - Component dùng chung cho hiển thị card chuồng
 * 
 * Sử dụng: 
 *   - Import vào HTML: <script src="js/coop-card-component.js"></script>
 *   - Render một card: CoopCardComponent.render(coop)
 *   - Render nhiều cards: CoopCardComponent.renderAll(coops)
 * 
 * Mapping status:
 *   - active/normal → online (màu xanh)
 *   - warning → warning (màu vàng)
 *   - inactive/error → error (màu đỏ)
 */

(function() {
    'use strict';

    window.CoopCardComponent = {
        /**
         * Tạo HTML cho một card chuồng
         * @param {Object} coop - Dữ liệu chuồng từ API
         * @param {Object} options - Tùy chọn hiển thị
         * @returns {string} HTML string
         */
        render: function(coop, options = {}) {
            if (!coop) return '';

            const showArea = options.showArea !== false;
            const showDevices = options.showDevices !== false;

            const status = coop.status || 'inactive';
            let statusClass, statusText;

            if (status === 'active' || status === 'normal') {
                statusClass = 'online';
                statusText = 'Bình thường';
            } else if (status === 'warning') {
                statusClass = 'warning';
                statusText = 'Cảnh báo';
            } else {
                statusClass = 'error';
                statusText = 'Lỗi';
            }

            const currentCount = coop.current_count || 0;
            const deviceCount = coop.devices ? coop.devices.length : (coop.device_count || 0);

            return `
                <div class="coop-summary-card ${statusClass}">
                    <div class="coop-summary-header">
                        <span class="coop-summary-name">${coop.name || 'Chuồng ' + coop.id}</span>
                        <span class="coop-summary-status ${statusClass}">${statusText}</span>
                    </div>
                    <div class="coop-summary-info">
                        <span><i class="fas fa-feather-alt"></i> ${currentCount} gà</span>
                        ${showDevices ? `<span><i class="fas fa-wifi"></i> ${deviceCount} thiết bị</span>` : ''}
                        ${showArea && coop.area ? `<span><i class="fas fa-ruler"></i> ${coop.area} m²</span>` : ''}
                    </div>
                </div>
            `;
        },

        /**
         * Render nhiều card chuồng
         * @param {Array} coops - Mảng dữ liệu chuồng
         * @param {Object} options - Tùy chọn hiển thị
         * @returns {string} HTML string
         */
        renderAll: function(coops, options = {}) {
            if (!Array.isArray(coops) || coops.length === 0) {
                return '<div class="text-muted p-3">Không có dữ liệu chuồng</div>';
            }
            return coops.map(coop => this.render(coop, options)).join('');
        },

        /**
         * Render card chuồng với link đến trang chi tiết
         * @param {Object} coop - Dữ liệu chuồng
         * @param {string} detailUrl - URL trang chi tiết
         * @returns {string} HTML string
         */
        renderWithLink: function(coop, detailUrl = '/coops') {
            if (!coop) return '';

            const status = coop.status || 'inactive';
            let statusClass, statusText;

            if (status === 'active' || status === 'normal') {
                statusClass = 'online';
                statusText = 'Bình thường';
            } else if (status === 'warning') {
                statusClass = 'warning';
                statusText = 'Cảnh báo';
            } else {
                statusClass = 'error';
                statusText = 'Lỗi';
            }

            const currentCount = coop.current_count || 0;
            const deviceCount = coop.devices ? coop.devices.length : (coop.device_count || 0);

            return `
                <a href="${detailUrl}${coop.id}" class="coop-summary-card ${statusClass}" style="text-decoration: none; display: block;">
                    <div class="coop-summary-header">
                        <span class="coop-summary-name">${coop.name || 'Chuồng ' + coop.id}</span>
                        <span class="coop-summary-status ${statusClass}">${statusText}</span>
                    </div>
                    <div class="coop-summary-info">
                        <span><i class="fas fa-feather-alt"></i> ${currentCount} gà</span>
                        <span><i class="fas fa-wifi"></i> ${deviceCount} thiết bị</span>
                    </div>
                </a>
            `;
        },

        /**
         * Render danh sách card chuồng với link
         * @param {Array} coops - Mảng dữ liệu chuồng
         * @param {string} detailUrl - URL trang chi tiết
         * @returns {string} HTML string
         */
        renderAllWithLinks: function(coops, detailUrl = '/coops') {
            if (!Array.isArray(coops) || coops.length === 0) {
                return '<div class="text-muted p-3">Không có dữ liệu chuồng</div>';
            }
            return coops.map(coop => this.renderWithLink(coop, detailUrl)).join('');
        }
    };

    console.log('✓ coop-card-component.js loaded - CoopCardComponent ready');
})();