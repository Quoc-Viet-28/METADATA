from typing import Optional, Dict, Any

from beanie import Link

from app.models.BaseModel import BaseModel
from app.models.device_model import Device
from app.models.ward_model import Ward


class Camera(BaseModel):
    name: str
    name_search: Optional[str]
    ip_camera: str
    httpPort: int
    user_name: str
    password: Optional[str]
    rtsp: Optional[str]
    address: Optional[str]
    coordinates: Optional[str]
    other_info: Dict[str, Any]
    ward: Optional[Link[Ward]]
    device: Link[Device]
    channel: int
    status: str
