from enum import Enum


class DeviceStatusEnum(Enum):
    START = "START"
    START_FAIL = "START_FAIL"
    ONLINE = "ONLINE"
    # - Lỗi xác thực: b'Error\r\nInvalid Authority!\r\n'
    ERROR_AUTHORITY = "ERROR_AUTHORITY"
    # - Lỗi sai loại thiết bị: b'Error\r\nBad Request!\r\n'
    ERROR_BAD_REQUEST = "ERROR_BAD_REQUEST"
    # - Lỗi mất kết nối: time.time() - dahuaDevice.time_receive_now > 20
    ERROR_CONNECTION = "ERROR_CONNECTION"

    #IP không đúng định dạng
    ERROR_IP = "ERROR_IP"

    STOP = "STOP"

    # khóa kết nối
    LOCK = "LOCK"
