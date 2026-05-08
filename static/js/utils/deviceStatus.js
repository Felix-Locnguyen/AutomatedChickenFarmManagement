const DEVICE_STATUS = {
    ACTIVE: {
        label: "Đang hoạt động",
        color: "#4CAF50",
        statusClass: "active"
    },
    ERROR: {
        label: "Lỗi",
        color: "#F44336",
        statusClass: "error"
    },
    CONNECTING: {
        label: "Đang kết nối",
        color: "#FFC107",
        statusClass: "connecting"
    },
    WAITING: {
        label: "Đang chờ được kết nối",
        color: "#9E9E9E",
        statusClass: "waiting"
    }
};

function getDeviceStatus(device) {
    if (device.is_active === 0 || device.is_active === false) return DEVICE_STATUS.WAITING;
    if (device.status === 'online' || device.status === 'connected') return DEVICE_STATUS.ACTIVE;
    if (device.status === 'connecting' || device.status === 'pending') return DEVICE_STATUS.CONNECTING;
    return DEVICE_STATUS.ERROR;
}
