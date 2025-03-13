from typing import Dict, Any, Optional
from beanie import Link

from app.constants.person_enum import SexPersonEnum
from app.models.BaseModel import BaseModel
from app.models.company_model import Company
from app.models.device_model import Device
from app.models.person_model import Person
from app.models.ward_model import Ward


class PersonCamera(BaseModel):
    device: Link[Device]
    # id cua person trong thiet bi
    person_device_id: str
    # id cua person trong he thong
    person: Link[Person]
    other_info: Dict[str, Any]
