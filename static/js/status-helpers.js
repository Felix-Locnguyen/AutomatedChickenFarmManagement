const DeviceStatus = {
    getText: (status, isActive) => {
        if (isActive === 0 || isActive === false) {
            return 'Thiết bị đã tắt';
        }
        const map = {
            'online': 'Hoạt động',
            'connected': 'Hoạt động',
            'connecting': 'Chờ kết nối',
            'pending': 'Chờ kết nối',
            'offline': 'Lỗi'
        };
        return map[status] || 'Lỗi';
    },
    getClass: (status, isActive) => {
        if (isActive === 0 || isActive === false) {
            return 'off';
        }
        const map = {
            'online': 'online',
            'connected': 'online',
            'connecting': 'waiting',
            'pending': 'waiting',
            'offline': 'offline'
        };
        return map[status] || 'offline';
    }
};