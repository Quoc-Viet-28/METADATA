from typing import Dict, Any, Optional

from beanie import Link

from app.constants.event_type_emum import EventTypeEnum
from app.models.BaseModel import BaseModel
from app.models.company_model import Company
from app.models.device_model import Device
from app.models.camera_model import Camera


class Event(BaseModel):
    event_type: EventTypeEnum
    data: Dict[str, Any]
    company: Link[Company]
    device: Link[Device]
    camera: Optional[Link[Camera]]=None

