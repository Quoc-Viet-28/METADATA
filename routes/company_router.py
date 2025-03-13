from typing import Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Query, Depends

from app.core.security import has_role
from app.dto.company_dto import CompanyCreate, CompanyUpdate
from app.services.company_service import company_service

router = APIRouter()
prefix = "/company"
tags = ["company"]

@router.post("/create", dependencies=[Depends(has_role("SYSTEM"))])
async def create(request: CompanyCreate):
    return await company_service.create(request)


@router.put("/{company_id}", dependencies=[Depends(has_role("SYSTEM"))])
async def update_company(company_id: PydanticObjectId, company_data: CompanyUpdate):
    return await company_service.update(company_id, company_data)


@router.get("/get-by-id/{company_id}")
async def get_by_id(company_id: PydanticObjectId):
    return await company_service.get_by_id(company_id)


@router.delete("/delete/{company_id}", dependencies=[Depends(has_role("SYSTEM"))])
async def delete(company_id: PydanticObjectId):
    return await company_service.delete(company_id)


@router.get("/get-all")
async def get_all(page: int = Query(0, ge=0), size: int = Query(10, gt=0), key_work: Optional[str] = Query(None),
                  is_full: bool = False):
    return await company_service.get_all(page, size, key_work, is_full)


@router.get("/get-count")
async def get_count(key_work: Optional[str] = Query(None)):
    return await company_service.get_count(key_work)
