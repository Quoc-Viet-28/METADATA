from beanie import Link

from app.models.BaseModel import BaseModel
from app.models.company_model import Company


class TypePerson(BaseModel):
    name: str
    name_search: str
    color: str
    description: str
    company: Link[Company]
