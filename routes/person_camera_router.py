import asyncio

from fastapi import APIRouter

from app.dto.person_camera_dto import PersonCameraCreateMutil, PersonCameraCreate, ManyPersonCameraCreateMutil
from app.services.person_camera_service import person_camera_services

router = APIRouter()
prefix = "/person-camera"
tags = ["person-camera"]

@router.get("/check-person-in-camera")
async def check_person_in_camera(id_person: str):
    return await person_camera_services.check_person_in_camera(id_person)

@router.post("/add-one-person-to-all-device")
async def add_one_person_to_all_device(request: PersonCameraCreateMutil):
    asyncio.create_task(person_camera_services.add_one_person_to_all_camera(request.id_person))
    return "Đang thêm người vào tất cả camera"


@router.post("/add-many-person-to-one-device")
async def add_many_person_to_one_device(request: ManyPersonCameraCreateMutil):
    asyncio.create_task(person_camera_services.add_many_person_to_one_device(request))
    return "Đang thêm nhiều người vào một camera"


@router.post("/add-person-to-device")
async def add_user_to_device(request: PersonCameraCreate):
    return await person_camera_services.add_user_to_device(request)


@router.delete("/delete-person-from-device")
async def delete_user_from_device(request: PersonCameraCreate):
    return await person_camera_services.delete_user_from_device(request)


@router.delete("/delete-person-from-all-device")
async def delete_user_from_all_device(request: PersonCameraCreateMutil):
    asyncio.create_task(person_camera_services.delete_one_person_from_all_camera(request))
    return "Đang xóa người khỏi tất cả camera"


@router.delete("/delete-many-person-from-device")
async def delete_many_user_from_device(request: ManyPersonCameraCreateMutil):
    asyncio.create_task(person_camera_services.delete_many_person_from_one_device(request))
    return "Đang xóa nhiều người khỏi một camera"

