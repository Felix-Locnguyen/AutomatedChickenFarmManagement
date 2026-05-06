/**
 * Donut Device Status Component
 * 
 * Reusable component for displaying device status donut chart
 * Used in: index.html, coop-list.html, device-list.html
 * 
 * API: GET /api/devices/status-stats
 * Response: { online: number, connecting: number, offline: number }
 */

(function() {
    'use strict';

    // Status mapping: API status -> chart segment
    const STATUS_MAPPING = {
        'online': 'hoatdong',
        'connecting': 'cho',
        'offline': 'loi'
    };

    // Chart colors (consistent across all pages)
    const CHART_COLORS = {
        'hoatdong': '#22c55e',  // Xanh - Hoạt động
        'cho': '#ffc107',        // Vàng - Chờ kết nối
        'loi': '#dc3545'        // Đỏ - Lỗi/Mất kết nối
    };

    // Store interval IDs for cleanup
    const refreshIntervals = {};

    /**
     * Convert API data to chart format
     * @param {object} apiData - { online, connecting, offline }
     * @returns {object} - { hoatdong, cho, loi }
     */
    function convertToChartData(apiData) {
        return {
            'hoatdong': apiData.online || 0,
            'cho': apiData.connecting || 0,
            'loi': apiData.offline || 0
        };
    }

    /**
     * Render donut chart with data
     * @param {string} elementId - ID of the donut chart container
     * @param {object} data - { hoatdong, cho, loi }
     */
    function renderDonutChart(elementId, data) {
        const container = document.getElementById(elementId);
        if (!container) {
            console.warn('Donut chart container not found:', elementId);
            return;
        }

        const segments = container.querySelectorAll('.donut-segment-coop');
        const total = (data.hoatdong || 0) + (data.cho || 0) + (data.loi || 0);
        
        if (total === 0) {
            segments.forEach(segment => {
                segment.style.strokeDasharray = '0 440';
            });
            const totalEl = container.querySelector('.donut-total-coop');
            if (totalEl) totalEl.textContent = '0';
            updateLegend(elementId, { hoatdong: 0, cho: 0, loi: 0 });
            return;
        }

        const circumference = 2 * Math.PI * 70;
        let offset = 0;
        const segmentOrder = ['hoatdong', 'cho', 'loi'];

        segments.forEach(segment => {
            const segmentType = segment.getAttribute('data-segment');
            if (!segmentOrder.includes(segmentType)) return;

            const count = data[segmentType] || 0;
            const percentage = total > 0 ? (count / total) : 0;
            const dashArray = percentage * circumference;

            let segmentName = '';
            if (segmentType === 'hoatdong') segmentName = 'Hoạt động';
            else if (segmentType === 'cho') segmentName = 'Chờ';
            else if (segmentType === 'loi') segmentName = 'Lỗi';

            segment.style.strokeDasharray = `${dashArray} ${circumference}`;
            segment.style.strokeDashoffset = -offset;
            segment.setAttribute('data-count', count);
            segment.setAttribute('data-percent', Math.round(percentage * 100));
            segment.setAttribute('data-name', segmentName);

            offset += dashArray;
        });

        const totalEl = container.querySelector('.donut-total-coop');
        if (totalEl) totalEl.textContent = total;

        updateLegend(elementId, data);
    }

    /**
     * Update legend with new data
     */
    function updateLegend(elementId, data) {
        const container = document.getElementById(elementId);
        if (!container) return;

        const legendItems = container.closest('.card-body')?.querySelectorAll('.legend-item-coop');
        if (!legendItems) return;

        legendItems.forEach(item => {
            const segmentType = item.getAttribute('data-segment');
            const count = data[segmentType] || 0;
            const textEl = item.querySelector('.legend-text-coop');
            
            if (textEl) {
                let label = '';
                if (segmentType === 'hoatdong') label = `Hoạt động (${count})`;
                else if (segmentType === 'cho') label = `Chờ (${count})`;
                else if (segmentType === 'loi') label = `Lỗi (${count})`;
                textEl.textContent = label;
            }
        });
    }

    /**
     * Load device status data from API and render chart
     * @param {string} elementId - ID of donut chart container
     * @param {number} refreshInterval - Auto-refresh interval in ms (default: 30000)
     * @returns {function} - Cleanup function
     */
    window.loadDeviceStatusDonut = function(elementId, refreshInterval = 30000) {
        if (refreshIntervals[elementId]) {
            clearInterval(refreshIntervals[elementId]);
        }

        const fetchAndRender = async function() {
            try {
                const response = await fetch('/api/devices/status-stats');
                if (!response.ok) throw new Error('Failed to fetch device stats');
                
                const apiData = await response.json();
                const chartData = convertToChartData(apiData);
                renderDonutChart(elementId, chartData);
            } catch (error) {
                console.error('Error loading device status donut:', error);
            }
        };

        fetchAndRender();

        if (refreshInterval > 0) {
            refreshIntervals[elementId] = setInterval(fetchAndRender, refreshInterval);
        }

        return function() {
            if (refreshIntervals[elementId]) {
                clearInterval(refreshIntervals[elementId]);
                delete refreshIntervals[elementId];
            }
        };
    };

    /**
     * Stop auto-refresh for a specific element
     */
    window.stopDeviceStatusDonutRefresh = function(elementId) {
        if (refreshIntervals[elementId]) {
            clearInterval(refreshIntervals[elementId]);
            delete refreshIntervals[elementId];
        }
    };

    console.log('✓ donut-device-status.js loaded');

})();