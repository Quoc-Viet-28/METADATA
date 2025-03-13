from typing import Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Query, Depends

from app.constants.device_status_enum import DeviceStatusEnum
from app.constants.device_type_enum import DeviceTypeEnum
from app.core.security import has_role, get_user_info, has_roles
from app.dto.device_dto import DeviceCreate, DeviceUpdate, DeviceUpdateStatus
from app.services.device_service import device_service

router = APIRouter()
prefix = "/device"
tags = ["device"]


@router.post("/create", dependencies=[Depends(has_roles(["SYSTEM", "ADMIN"]))])
async def create(request: DeviceCreate, user=Depends(get_user_info())):
    return await device_service.create(request, user)


@router.put("/{id}", dependencies=[Depends(has_roles(["SYSTEM", "ADMIN"]))])
async def update(id: PydanticObjectId, data: DeviceUpdate, user=Depends(get_user_info())):
    return await device_service.update(id, data, user)


@router.patch("/{id}", dependencies=[Depends(has_roles(["SYSTEM", "ADMIN"]))])
async def update_status(id: PydanticObjectId, status: DeviceUpdateStatus, user=Depends(get_user_info())):
    return await device_service.set_status(id, status, user)


@router.get("/get-by-id/{id}")
async def get_by_id(id: PydanticObjectId):
    return await device_service.get_by_id(id)


# @router.delete("/delete/{id}")
# async def delete(id: PydanticObjectId):
#     return await device_service.delete(id)


@router.get("/get-all")
async def get_all(device_type: DeviceTypeEnum, page: int = Query(0, ge=0), size: int = Query(10, gt=0),
                  key_work: Optional[str] = Query(None),
                  is_full: bool = False, status: Optional[str] = Query(None),
                  id_company: Optional[PydanticObjectId] = Query(None),
                  user=Depends(get_user_info())):
    return await device_service.get_all(device_type, page, size, key_work, is_full, status, id_company, user)


@router.get("/get-count")
async def get_count(device_type: DeviceTypeEnum, key_work: Optional[str] = Query(None),
                    status: Optional[str] = Query(None),
                    id_company: Optional[PydanticObjectId] = Query(None),
                    user=Depends(get_user_info())):
    return await device_service.get_count(device_type, key_work, status, id_company, user)


@router.get("/get-device-face")
async def get_device_face(id_person: PydanticObjectId, page: int = Query(0, ge=0), size: int = Query(10, gt=0),
                          key_work: Optional[str] = Query(None)):
    return await device_service.get_device_face(id_person, page, size, key_work)


@router.get("/get-count-device-face")
async def get_count_device_face(id_person: PydanticObjectId, key_work: Optional[str] = Query(None)):
    return await device_service.get_count_device_face(id_person, key_work)
