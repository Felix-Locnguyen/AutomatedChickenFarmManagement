const DeviceStatus = {
    getText: (status, isActive) => {
        const info = getDeviceStatus({ status: status, is_active: isActive });
        return info.label;
    },
    getClass: (status, isActive) => {
        const info = getDeviceStatus({ status: status, is_active: isActive });
        return info.statusClass;
    }
};