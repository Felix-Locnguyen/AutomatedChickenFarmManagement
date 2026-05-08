const DeviceStatus = {
    getText: (status) => {
        const map = {
            'online': 'Hoạt động',
            'connected': 'Hoạt động',
            'connecting': 'Chờ kết nối',
            'pending': 'Chờ kết nối',
            'offline': 'Lỗi'
        };
        return map[status] || 'Lỗi';
    },
    getClass: (status) => {
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