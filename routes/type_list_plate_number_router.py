from typing import Optional
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends
from app.core.security import get_user_info
from app.dto.type_list_plate_number_dto import TypeListPlateNumberCreate, TypeListPlateNumberUpdate
from app.services.type_list_plate_number_service import type_list_plate_number_service
router = APIRouter()
prefix = "/type-list-plate-number"
tags = ["type-list-plate-number"]

@router.post("/create")
async def create(request: TypeListPlateNumberCreate, user=Depends(get_user_info())):
    return await type_list_plate_number_service.create(request, user)
@router.put("/update")
async def update(request: TypeListPlateNumberUpdate, user=Depends(get_user_info())):
    return await type_list_plate_number_service.update(request, user)
@router.get("/get-all")
async def get_all(id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info()), keyword: Optional[str] = None, page: int = 0, size: int = 10, color: Optional[str] = None, type_vehicle: Optional[str] = None, type_plate_number: Optional[PydanticObjectId] = None):
    return await type_list_plate_number_service.get_by_company(id_company, keyword, page, size, user, color, type_vehicle, type_plate_number)
@router.get("/get-count")
async def get_count(id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info()), keyword: Optional[str] = None, color: Optional[str] = None, type_vehicle: Optional[str] = None ,type_plate_number: Optional[PydanticObjectId] = None):
    return await type_list_plate_number_service.get_count(id_company, keyword, user, color, type_vehicle, type_plate_number)