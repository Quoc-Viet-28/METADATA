from typing import Optional

from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
