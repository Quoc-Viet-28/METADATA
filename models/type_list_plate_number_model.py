from beanie import Link
from app.models.BaseModel import BaseModel
from app.models.company_model import Company
from app.models.type_platenumber_model import TypePlateNumber


class TypeListPlateNumber(BaseModel):
    name: str
    name_search: str
    color: str
    type_vehicle: str
    type_plate_number: Link[TypePlateNumber]
    company: Link[Company]