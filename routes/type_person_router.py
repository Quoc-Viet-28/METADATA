from typing import Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.core.security import get_user_info
from app.dto.type_person_dto import TypePersonCreate, TypePersonUpdate
from app.services.type_person_service import type_person_service

router = APIRouter()
prefix = "/type-person"
tags = ["type-person"]


@router.post("/create")
async def create(request: TypePersonCreate, user=Depends(get_user_info())):
    return await type_person_service.create(request, user)


@router.put("/update")
async def update(request: TypePersonUpdate, user=Depends(get_user_info())):
    return await type_person_service.update(request, user)


@router.get("/get-all")
async def get_all(id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info()),
                  keyword: Optional[str] = None, page: int = 0, size: int = 10):
    return await type_person_service.get_by_company(id_company, keyword, page, size, user)


@router.get("/get-count")
async def get_count(id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info()),
                    keyword: Optional[str] = None):
    return await type_person_service.get_count(id_company, keyword, user)
