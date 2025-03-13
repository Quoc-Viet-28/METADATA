from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException

from app.dto.camera_dto import CameraCreate, CameraUpdate, GetRTSP
from app.services.camera_service import camera_service
from app.utils.camera_utils import get_retsp_onvif

router = APIRouter()
prefix = "/camera"
tags = ["camera"]


@router.post("/create")
async def create_camera(request: CameraCreate):
    return await camera_service.create(request)


@router.put("/update")
async def update_camera(request: CameraUpdate):
    return await camera_service.update(request)


@router.get("/sync-camera")
async def sync_camera(device_id: PydanticObjectId):
    return await camera_service.sync_camera(device_id)


@router.get("/get-channel-empty")
async def get_channel_empty(device_id: PydanticObjectId):
    return await camera_service.get_channel_empty(device_id)


@router.get("/get-camera-by-device")
async def get_camera_by_device(device_id: PydanticObjectId):
    return await camera_service.get_camera_by_device(device_id)


@router.post("/get-rtsp")
def get_rtsp(request: GetRTSP):
    rtsp = get_retsp_onvif(request.ip_camera, request.port, request.user_name, request.password)
    if not rtsp:
        raise HTTPException(status_code=403, detail="Không thể lấy RTSP từ camera")
    return rtsp
