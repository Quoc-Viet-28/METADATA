from typing import Optional, Dict, Any

from beanie import Link

from app.constants.device_status_enum import DeviceStatusEnum
from app.constants.device_type_enum import DeviceTypeEnum
from app.models.BaseModel import BaseModel
from app.models.company_model import Company
from app.models.ward_model import Ward

class Device(BaseModel):
    name: str
    name_search: Optional[str]
    device_type: DeviceTypeEnum
    ip_device: str
    port: int
    user_name: str
    password: str
    rtsp: Optional[str]
    address: Optional[str]
    coordinates: Optional[str]
    other_info: Dict[str, Any]
    ward: Optional[Link[Ward]]
    company: Link[Company]
    is_support_face: bool
    status: DeviceStatusEnum = DeviceStatusEnum.START
    protocol: Optional[str] = "http"
