from typing import Dict, Any

from beanie import Link

from app.constants.authorization_enum import AuthorizationEnum
from app.constants.event_type_emum import EventTypeEnum
from app.models.BaseModel import BaseModel
from app.models.company_model import Company


class WebHook(BaseModel):
    name: str
    name_search: str
    url: str
    event_type: EventTypeEnum
    company: Link[Company]
    authorization: AuthorizationEnum
    other_authorization: Dict[str, Any]
    is_active: bool
