from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel

class TypeListPlateNumberCreate(BaseModel):
    name: str
    color: str
    type_vehicle: str
    id_type_plate_number: Optional[PydanticObjectId] = None
    id_company: Optional[PydanticObjectId] = None

class TypeListPlateNumberUpdate(BaseModel):
    id: PydanticObjectId
    name: Optional[str] = None
    color: Optional[str] = None
    type_vehicle: Optional[str] = None
    id_type_plate_number: Optional[PydanticObjectId] = None
    id_company: Optional[PydanticObjectId] = None