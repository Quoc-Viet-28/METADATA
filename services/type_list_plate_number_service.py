import re

from beanie import PydanticObjectId

from app.dto.type_list_plate_number_dto import TypeListPlateNumberCreate, TypeListPlateNumberUpdate
from app.models.type_list_plate_number_model import TypeListPlateNumber
from app.models.type_platenumber_model import TypePlateNumber
from app.utils.common_utils import get_company
import unidecode
class TypeListPlateNumberService:
    async def create(self, request: TypeListPlateNumberCreate, user):
        company = await get_company(user, request.id_company)
        name_search = unidecode.unidecode(request.name).lower()
        type_list_plate_number = TypeListPlateNumber(
            name=request.name,
            color=request.color,
            type_vehicle=request.type_vehicle,
            type_plate_number=request.id_type_plate_number,
            company=company,
            name_search=name_search
        )
        await type_list_plate_number.insert()
        return type_list_plate_number
    async def update(self, request: TypeListPlateNumberUpdate, user):
        type_list_plate_number= await TypeListPlateNumber.get(request.id)
        update_data=request.dict(exclude_unset=True, exclude={"id_company", "id", "id_type_plate_number"})
        for field, value in update_data.items():
            setattr(type_list_plate_number, field, value)
        if request.name:
            type_list_plate_number.name_search = unidecode.unidecode(request.name).lower()
        if request.id_type_plate_number:
            type_list_plate_number.type_plate_number = await TypePlateNumber.find_one({"_id":request.id_type_plate_number})
        if request.id_company:
            company = await get_company(user, request.id_company)
            type_list_plate_number.company = company
        await type_list_plate_number.replace()
        return type_list_plate_number
    async def get_by_company(self, id_company, keyword, page, size, user, color, type_vehicle, type_plate_number):
        company = await get_company(user, id_company)
        query = {
            "$and": [
                {"company": {"$ref": "Company", "$id": company.id}}
            ]
        }
        if keyword:
            keyword = unidecode.unidecode(keyword).lower()
            query["$and"].append({"name_search": {"$regex": keyword, "$options": "i"}})
        if color:
            color = unidecode.unidecode(color).lower()
            query["$and"].append({"color": {"$regex": color, "$options": "i"}})
        if type_plate_number:
            query["$and"].append({"type_plate_number.$id": type_plate_number})
        if type_vehicle:
            type_vehicle = unidecode.unidecode(type_vehicle).lower()
            query["$and"].append({"type_vehicle": {"$regex": type_vehicle, "$options": "i"}})
        return await TypeListPlateNumber.find(query).skip(page * size).limit(size).sort("-created_at").to_list()
    async def get_count(self, id_company, keyword, user, color, type_vehicle, type_plate_number):
        company = await get_company(user, id_company)
        query = {
            "$and": [
                {"company": {"$ref": "Company", "$id": company.id}}
            ]
        }
        if keyword:
            keyword = unidecode.unidecode(keyword).lower()
            query["$and"].append({"name_search": {"$regex": keyword, "$options": "i"}})
        if color:
            color = unidecode.unidecode(color).lower()
            query["$and"].append({"color": {"$regex": color, "$options": "i"}})
        if type_plate_number:
            query["$and"].append({"type_plate_number.$id": type_plate_number})
        if type_vehicle:
            type_vehicle = unidecode.unidecode(type_vehicle).lower()
            query["$and"].append({"type_vehicle": {"$regex": type_vehicle, "$options": "i"}})
        return await TypeListPlateNumber.find(query).count()
type_list_plate_number_service = TypeListPlateNumberService()