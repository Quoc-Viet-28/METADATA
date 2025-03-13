from app.models.BaseModel import BaseModel
from beanie import Link

from app.models.province_model import Province


class District(BaseModel):
    id: str
    name: str
    name_search: str
    code: str
    province: Link[Province]