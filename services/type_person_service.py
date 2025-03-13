import unidecode

from app.dto.type_person_dto import TypePersonCreate, TypePersonUpdate
from app.models.type_person_model import TypePerson
from app.utils.common_utils import get_company


class TypePersonService:

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

        return await TypePerson.find(query).skip(page * size).limit(size).sort("-created_at").to_list()

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

        return await TypePerson.find(query).count()

    async def create(self, request: TypePersonCreate, user):
        company = await get_company(user, request.id_company)
        name_search = unidecode.unidecode(request.name).lower()
        type_person = TypePerson(
            name=request.name,
            color=request.color,
            description=request.description,
            company=company,
            name_search=name_search
        )
        await type_person.insert()
        return type_person

    async def update(self, request: TypePersonUpdate, user):
        type_person = await TypePerson.get(request.id)

        update_data = request.dict(exclude_unset=True,
                                   exclude={"id_company", "id"})
        for field, value in update_data.items():
            setattr(type_person, field, value)

        if request.name:
            type_person.name_search = unidecode.unidecode(request.name).lower()

        if request.id_company:
            company = await get_company(user, request.id_company)
            type_person.company = company

        await type_person.replace()
        return type_person


type_person_service = TypePersonService()
