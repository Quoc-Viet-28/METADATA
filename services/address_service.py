import unidecode
from beanie import PydanticObjectId
from fastapi import HTTPException, status, Query
from app.models.province_model import Province
from app.models.district_model import District
from app.models.ward_model import Ward
import re


class AddressService:
    def __init__(self):
        pass

    async def get_province_by_id(self, province_id: str):
        province = await Province.get(province_id)
        if not province:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tỉnh")
        return province

    async def get_all_province(self, page: int = Query(0, ge=0), size: int = Query(10, gt=0), key_work=None,
                               is_full: bool = False):
        query = []
        if key_work:
            key_work = unidecode.unidecode(key_work).lower()
            regex = re.compile(f".*{key_work}.*", re.IGNORECASE)
            query.append({"name_search": {"$regex": regex}})
            query.append({"code": {"$regex": regex}})
        if is_full:
            provinces = await Province.find({} if not query else {"$or": query}).sort("-created_at").to_list()
        else:
            provinces = await Province.find({} if not query else {"$or": query}).skip(page * size).limit(size).sort(
                "-created_at").to_list()
        return provinces

    async def get_district_by_province_ID(self, province_id: str, key_work: str | None = None):
        query = []
        if key_work:
            key_work = unidecode.unidecode(key_work).lower()
            regex = re.compile(f".*{key_work}.*", re.IGNORECASE)
            query.append({"name_search": {"$regex": regex}})
            query.append({"code": {"$regex": regex}})
        districts = await District.find(
            {"province.$id": province_id} if not query else {"province.$id": province_id, "$or": query}).to_list()
        if not districts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy các quận"
            )
        return districts

    async def get_ward_by_district_ID(self, district_id: str, key_work: str | None = None):
        query = []
        if key_work:
            key_work = unidecode.unidecode(key_work).lower()
            regex = re.compile(f".*{key_work}.*", re.IGNORECASE)
            query.append({"name_search": {"$regex": regex}})
            query.append({"code": {"$regex": regex}})
        wards = await Ward.find(
            {"district.$id": district_id} if not query else {"district.$id": district_id, "$or": query}).to_list()
        if not wards:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy các phường"
            )
        return wards


address_service = AddressService()
