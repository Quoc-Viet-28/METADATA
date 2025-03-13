import unidecode

from app.dto.type_plate_number_dto import TypePlateNumberCreate, TypePlateNumberUpdate
from app.models.type_platenumber_model import TypePlateNumber
from app.utils.common_utils import get_company


class TypePlateNumberService:

    async def get_by_company(self, id_company, keyword, page, size, user):
        company = await get_company(user, id_company)
        query = {
            "$and": [
                {"company": {"$ref": "Company", "$id": company.id}}
            ]
        }
        if keyword:
            keyword = unidecode.unidecode(keyword).lower()
            query["$and"].append({"name_search": {"$regex": keyword, "$options": "i"}})

        return await TypePlateNumber.find(query).skip(page * size).limit(size).sort("-created_at").to_list()

    async def get_count(self, id_company, keyword, user):
        company = await get_company(user, id_company)
        query = {
            "$and": [
                {"company": {"$ref": "Company", "$id": company.id}}
            ]
        }
        if keyword:
            keyword = unidecode.unidecode(keyword).lower()
            query["$and"].append({"name_search": {"$regex": keyword, "$options": "i"}})

        return await TypePlateNumber.find(query).count()

    async def create(self, request: TypePlateNumberCreate, user):
        company = await get_company(user, request.id_company)
        name_search = unidecode.unidecode(request.name).lower()
        type_plate_number = TypePlateNumber(
            name=request.name,
            color=request.color,
            description=request.description,
            company=company,
            name_search=name_search
        )
        await type_plate_number.insert()
        return type_plate_number

    async def update(self, request: TypePlateNumberUpdate, user):
        type_plate_number = await TypePlateNumber.get(request.id)

        update_data = request.dict(exclude_unset=True,
                                   exclude={"id_company", "id"})
        for field, value in update_data.items():
            setattr(type_plate_number, field, value)

        if request.name:
            type_plate_number.name_search = unidecode.unidecode(request.name).lower()

        if request.id_company:
            company = await get_company(user, request.id_company)
            type_plate_number.company = company

        await type_plate_number.replace()
        return type_plate_number


type_plate_number_service = TypePlateNumberService()
