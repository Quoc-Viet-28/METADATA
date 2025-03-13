from typing import Optional, Dict, Any

from beanie import PydanticObjectId
from pydantic import BaseModel

from app.constants.authorization_enum import AuthorizationEnum
from app.constants.event_type_emum import EventTypeEnum


class AuthorizationCreate(BaseModel):
    name: str
    url: str
    event_type: EventTypeEnum
    id_company: Optional[PydanticObjectId] = None
    authorization: AuthorizationEnum
    other_authorization: Dict[str, Any]


class AuthorizationUpdate(BaseModel):
    id: PydanticObjectId
    name: Optional[str] = None
    url: Optional[str] = None
    event_type: Optional[EventTypeEnum] = None
    id_company: Optional[PydanticObjectId] = None
    authorization: Optional[AuthorizationEnum] = None
    other_authorization: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
