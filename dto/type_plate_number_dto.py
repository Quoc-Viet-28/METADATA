from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel


class TypePlateNumberCreate(BaseModel):
    name: str
    color: str
    description: Optional[str] = None
    id_company: Optional[PydanticObjectId] = None


class TypePlateNumberUpdate(BaseModel):
    id: PydanticObjectId
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    id_company: Optional[PydanticObjectId] = None
