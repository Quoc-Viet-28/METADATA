from typing import Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.core.security import get_user_info
from app.dto.type_plate_number_dto import TypePlateNumberCreate, TypePlateNumberUpdate
from app.services.type_platenumber_service import type_plate_number_service

router = APIRouter()
prefix = "/type-plate-number"
tags = ["type-plate-number"]


@router.post("/create")
async def create(request: TypePlateNumberCreate, user=Depends(get_user_info())):
    return await type_plate_number_service.create(request, user)


@router.put("/update")
async def update(request: TypePlateNumberUpdate, user=Depends(get_user_info())):
    return await type_plate_number_service.update(request, user)


@router.get("/get-all")
async def get_all(id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info()),
                  keyword: Optional[str] = None, page: int = 0, size: int = 10):
    return await type_plate_number_service.get_by_company(id_company, keyword, page, size, user)


@router.get("/get-count")
async def get_count(id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info()),
                    keyword: Optional[str] = None):
    return await type_plate_number_service.get_count(id_company, keyword, user)
