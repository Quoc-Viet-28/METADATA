from typing import Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query

from app.core.security import get_user_info
from app.dto.authorization_dto import AuthorizationCreate, AuthorizationUpdate
from app.services.webhook_service import WebHookService

router = APIRouter()
prefix = "/webhook"
tags = ["webhook"]
webHookService = WebHookService()


@router.post("/create")
async def create_webhook(request: AuthorizationCreate, user=Depends(get_user_info())):
    return await webHookService.create(request, user)


@router.put("/update")
async def update_webhook(request: AuthorizationUpdate,user=Depends(get_user_info())):
    return await webHookService.update(request, user)


@router.delete("/delete/{id}")
async def delete_webhook(id: PydanticObjectId):
    return await webHookService.delete(id)


@router.get("/get-all")
async def get_all(page: int = Query(0, ge=0), size: int = Query(10, gt=0), key_work: Optional[str] = Query(None),
                  id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info())):
    return await webHookService.get_all(page, size, key_work, id_company,user)


@router.get("/get-count")
async def get_count(key_work: Optional[str] = Query(None), id_company: Optional[PydanticObjectId] = None, user=Depends(get_user_info())):
    return await webHookService.get_count(key_work, id_company, user)
