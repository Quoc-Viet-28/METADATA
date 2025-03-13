import re

import unidecode
from beanie import PydanticObjectId
from fastapi import HTTPException, status, Query

from app.dto.company_dto import CompanyCreate, CompanyUpdate
from app.models.company_model import Company


class CompanyService:
    def __init__(self):
        pass

    async def create(self, company: CompanyCreate):
        company_exist = await Company.find_one({"name": company.name})
        if company_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên công ty đã tồn tại",
            )
        new_company = Company(**company.dict(), name_search=unidecode.unidecode(company.name).lower())
        await new_company.insert()
        return new_company

    async def update(self, company_id: PydanticObjectId, company_data: CompanyUpdate):
        company = await Company.get(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy công ty")

        # check company name exist
        company_exist = await Company.find_one({"$and": [{"name": company_data.name}, {"_id": {"$ne": company_id}}]})
        if company_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên công ty đã tồn tại",
            )

        # Update only fields that are provided
        update_data = company_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)
        if company_data.name:
            company.name_search = unidecode.unidecode(company_data.name).lower()
        await company.replace()  # Automatically triggers `before_event` to update `updated_at`
        return company

    async def get_by_id(self, company_id: PydanticObjectId):
        company = await Company.get(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy công ty")
        return company

    async def delete(self, company_id: PydanticObjectId):
        company = await Company.get(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy công ty")
        await company.delete()
        return {"message": "Xóa công ty thành công"}

    async def get_all(self, page: int = Query(0, ge=0), size: int = Query(10, gt=0), key_work=None,
                      is_full: bool = False):
        query = []
        if key_work:
            key_work = unidecode.unidecode(key_work).lower()
            regex = re.compile(f".*{key_work}.*", re.IGNORECASE)
            query.append({"name_search": {"$regex": regex}})
            query.append({"phone_number": {"$regex": regex}})

        if is_full:
            companies = await Company.find({} if not query else {"$or": query}).sort("-created_at").to_list()
        else:
            companies = await Company.find({} if not query else {"$or": query}).skip(page * size).limit(size).sort(
                "-created_at").to_list()

        return companies

    async def get_count(self, key_work=None):
        query = []
        if key_work:
            key_work = unidecode.unidecode(key_work).lower()
            regex = re.compile(f".*{key_work}.*", re.IGNORECASE)
            query.append({"name_search": {"$regex": regex}})
            query.append({"phone_number": {"$regex": regex}})

        count = await Company.find({} if not query else {"$or": query}).count()
        return count


company_service = CompanyService()
