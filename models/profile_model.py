from beanie import Link

from app.models.BaseModel import BaseModel
from app.models.company_model import Company


class Profile(BaseModel):
    id_user: str
    company:Link[Company]