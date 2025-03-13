from app.models.BaseModel import BaseModel


class Province(BaseModel):
    id: str
    name: str
    name_search: str
    code: str
