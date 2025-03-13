from app.models.BaseModel import BaseModel
from beanie import Link

from app.models.district_model import District


class Ward(BaseModel):
    id: str
    name: str
    name_search: str
    code: str
    district: Link[District]