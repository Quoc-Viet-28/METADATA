from datetime import datetime
from typing import Dict, Any, Optional
from beanie import Link

from app.constants.person_enum import SexPersonEnum
from app.models.BaseModel import BaseModel
from app.models.company_model import Company
from app.models.type_person_model import TypePerson
from app.models.ward_model import Ward


class Person(BaseModel):
    name: str
    name_search: str
    birthday: Optional[datetime] = None
    type_person: Optional[Link[TypePerson]]
    sex: Optional[SexPersonEnum] = SexPersonEnum.UNKNOWN
    address: Optional[str]
    ward: Optional[Link[Ward]]
    image: str
    other_info: Optional[Dict[str, Any]]
    company: Link[Company]