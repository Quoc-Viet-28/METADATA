from beanie import PydanticObjectId
from fastapi import APIRouter, Query
from typing import Optional

from app.services.address_service import address_service

router = APIRouter()
prefix = "/address"
tags = ["address"]

@router.get("/get_province_by_id/{province_id}")
async def get_province_by_id(province_id: str):
    return await address_service.get_province_by_id(province_id)
@router.get("/get_all_province")
async def get_all_province(page: int = Query(0, ge=0), size: int = Query(64, gt=0), key_work: Optional[str] = Query(None),
                  is_full: bool = False):
    return await address_service.get_all_province(page, size, key_work, is_full)
@router.get("/get_district_by_province_id/{province_id}")
async def get_district_by_province_id(province_id: str, key_work: Optional[str] = Query(None)):
    return await address_service.get_district_by_province_ID(province_id, key_work)
@router.get("/get_ward_by_district_id/{district_id}")
async def get_ward_by_district_id(district_id: str, key_work: Optional[str] = Query(None)):
    return await address_service.get_ward_by_district_ID(district_id, key_work)



