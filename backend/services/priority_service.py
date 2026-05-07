"""
Priority Service - Tính toán mức độ ưu tiên cho chuồng
"""

from models import Environment, Device, CoopDevice, Alert, db


def get_coop_priority(coop):
    """
    Tính toán mức độ ưu tiên của chuồng.
    Returns: 1 (cao nhất - cảnh báo nghiêm trọng), 2 (thiết bị lỗi), 3 (bình thường)
    """
    # Ưu tiên 1: Cảnh báo nghiêm trọng (vượt ngưỡng nhiệt độ/độ ẩm/nước/thức ăn)
    latest_env = Environment.query.filter_by(
        coop_id=coop.id
    ).order_by(Environment.recorded_at.desc()).first()

    if latest_env:
        # Kiểm tra nhiệt độ
        if latest_env.temperature is not None:
            if latest_env.temperature < coop.temp_min or latest_env.temperature > coop.temp_max:
                return 1
        # Kiểm tra độ ẩm
        if latest_env.humidity is not None:
            if latest_env.humidity < coop.humidity_min or latest_env.humidity > coop.humidity_max:
                return 1
        # Kiểm tra thức ăn dưới ngưỡng
        if latest_env.feed_level is not None and latest_env.feed_level < coop.feed_threshold:
            return 1
        # Kiểm tra nước dưới ngưỡng
        if latest_env.water_level is not None and latest_env.water_level < coop.water_threshold:
            return 1

    # Kiểm tra cảnh báo critical chưa xử lý
    critical_alert = Alert.query.filter(
        Alert.coop_id == coop.id,
        Alert.is_resolved == False,
        Alert.level == 'critical'
    ).first()
    if critical_alert:
        return 1

    # Ưu tiên 2: Thiết bị mất kết nối/chờ kết nối hoặc coop warning
    priority = 3

    # Lấy thiết bị trong chuồng
    coop_devices = CoopDevice.query.filter_by(coop_id=coop.id, deleted=False).all()
    device_ids = [cd.device_id for cd in coop_devices]

    if device_ids:
        offline_count = Device.query.filter(
            Device.id.in_(device_ids),
            Device.status.in_(['offline', 'connecting']),
            Device.deleted == False
        ).count()
        if offline_count > 0:
            priority = 2

    # Kiểm tra trạng thái chuồng warning
    if coop.status == 'warning':
        priority = 2

    # Kiểm tra cảnh báo warning chưa xử lý
    warning_alert = Alert.query.filter(
        Alert.coop_id == coop.id,
        Alert.is_resolved == False,
        Alert.level == 'warning'
    ).first()
    if warning_alert:
        priority = 2

    return priority
