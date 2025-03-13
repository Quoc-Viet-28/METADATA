from typing import Optional

from app.models.BaseModel import BaseModel


class Company(BaseModel):
    name: str
    name_search: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
