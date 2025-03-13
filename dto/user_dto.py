from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    id_company: Optional[PydanticObjectId] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    id_company: Optional[PydanticObjectId] = None
    id_user: Optional[str] = None


class ResetPassword(BaseModel):
    user_id: Optional[str] = None
    password: str
    temporary: bool


class AssignRole(BaseModel):
    user_id: str
    role: str

class EnabledUser(BaseModel):
    user_id: str
    enabled: bool