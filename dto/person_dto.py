from datetime import datetime
from typing import Optional, Dict, Any

from beanie import PydanticObjectId, Link
from pydantic import BaseModel, field_validator

from app.constants.person_enum import SexPersonEnum, TypeImagePersonEnum
from app.models.type_person_model import TypePerson


class PersonCreate(BaseModel):
    name: str
    sex: Optional[SexPersonEnum] = None
    address: Optional[str] = None
    id_ward: Optional[str] = None
    id_type_person: Optional[PydanticObjectId] = None
    image: str
    type_image: Optional[TypeImagePersonEnum] = TypeImagePersonEnum.LINK
    is_add_all_camera: Optional[bool] = False
    other_info: Optional[Dict[str, Any]]= None
    id_company: Optional[PydanticObjectId] = None
    birthday: Optional[datetime] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    sex: Optional[SexPersonEnum] = None
    address: Optional[str] = None
    id_ward: Optional[str] = None
    image: Optional[str] = None
    type_image: Optional[TypeImagePersonEnum] = None
    other_info: Optional[Dict[str, Any]] = None
    id_type_person: Optional[PydanticObjectId] = None
    birthday: Optional[datetime] = None


class PersonResponse(BaseModel):
    id: PydanticObjectId
    name: str
    birthday: Optional[datetime] = None
    sex: SexPersonEnum
    address: Optional[str] = None
    image: str
    other_info: Dict[str, Any]
    type_person: Link[TypePerson]
    created_at: datetime
    updated_at: Optional[datetime] = None



