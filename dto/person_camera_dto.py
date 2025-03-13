from beanie import PydanticObjectId
from pydantic import BaseModel


class PersonCameraCreateMutil(BaseModel):
    id_person: PydanticObjectId

class ManyPersonCameraCreateMutil(BaseModel):
    id_device: PydanticObjectId


class PersonCameraCreate(BaseModel):
    id_device: PydanticObjectId
    id_person: PydanticObjectId
