from fastapi import APIRouter, Query, Depends
from beanie import PydanticObjectId
from typing import Optional

from app.core.security import get_user_info
from app.services.event_service import event_service

router = APIRouter()
prefix = "/event"
tags = ["event"]

@router.get("/get-plate-by-event-ANPR")
async def get_plate_by_event_ANPR(id_company:PydanticObjectId, user=Depends(get_user_info()),page: int = Query(0, ge=0), size: int = Query(10, gt=0), plate: Optional[str] = None, color_vehicle: Optional[str]=None,color_plate: Optional[str] = None,vehicle_type: Optional[str] = None, name_logo_vehicle: Optional[str] = None):
    return await event_service.get_data_by_event_ANPR(id_company, user, page, size, plate,color_vehicle,color_plate,vehicle_type,name_logo_vehicle)

@router.get("/get-count-by-event-ANPR")
async def get_count_by_event_ANPR(id_company: PydanticObjectId, user=Depends(get_user_info()), plate: Optional[str] = None, color_vehicle: Optional[str] = None, color_plate: Optional[str] = None, vehicle_type: Optional[str] = None, name_logo_vehicle: Optional[str] = None):
    return await event_service.get_count_by_event_ANPR(id_company, user, plate, color_vehicle, color_plate, vehicle_type, name_logo_vehicle)

@router.get("/get-count-by-event-METADATA")
async def get_count_by_event_METADATA(id_company: PydanticObjectId, user=Depends(get_user_info()), plate: Optional[str] = None, color_vehicle: Optional[str] = None, color_plate: Optional[str] = None, vehicle_type: Optional[str] = None, name_logo_vehicle: Optional[str] = None, color_tshirt: Optional[str] = None,
                                      color_pants: Optional[str] = None, helmet: Optional[str] = None, raincoat: Optional[str] = None,mask: Optional[str] = None):
    return await event_service.get_count_by_event_METADATA(id_company, user, plate, color_vehicle, color_plate, vehicle_type, name_logo_vehicle,color_tshirt,color_pants,helmet,raincoat,mask)

@router.get("/get-plate-by-event-METADATA")
async def get_plate_by_event_METADATA(id_company: PydanticObjectId, user=Depends(get_user_info()),page: int = Query(0, ge=0), size: int = Query(10, gt=0), plate: Optional[str] = None, color_vehicle: Optional[str]=None,
                                      color_plate: Optional[str] = None,vehicle_type: Optional[str] = None, name_logo_vehicle: Optional[str] = None, color_tshirt: Optional[str] = None,
                                      color_pants: Optional[str] = None, helmet: Optional[str] = None, raincoat: Optional[str] = None,mask: Optional[str] = None):
    return await event_service.get_data_by_event_METADATA(id_company, user, page, size, plate,color_vehicle,color_plate,vehicle_type,name_logo_vehicle,color_tshirt,color_pants,helmet,raincoat,mask)

@router.get("/get-face-by-id")
async def get_face_by_id(id_company: PydanticObjectId, user=Depends(get_user_info()),page: int = Query(0, ge=0), size: int = Query(10, gt=0), id_card_person : Optional[str]= None, name_person : Optional[str]= None):
    return await event_service.get_data_by_event_FACE(id_company, user, page, size, id_card_person, name_person)

@router.get("/get-count-face-by-id")
async def get_count_face_by_id(id_company: PydanticObjectId, user=Depends(get_user_info()), id_card_person : Optional[str]= None, name_person : Optional[str]= None):
    return await event_service.get_count_by_event_FACE(id_company, user, id_card_person, name_person)

@router.get("/get-image-by-ip-camera-from-crossline")
async def get_image_by_ip_camera_from_crossline(id_company: PydanticObjectId, id_device: PydanticObjectId, ip_camera: str,
                                                user=Depends(get_user_info()), page: int = Query(0, ge=0), size: int = Query(10, gt=0),
                                                time_left_to_right: Optional[str] = None, time_right_to_left: Optional[str] = None,total_time: Optional[int] = None):
    return await event_service.get_image_by_ip_camera_from_crossline(id_company, id_device, ip_camera, user, page, size, time_left_to_right, time_right_to_left, total_time)
@router.get("/get-count-image-by-ip-camera-from-crossline")
async def get_count_image_by_ip_camera_from_crossline(id_company: PydanticObjectId, id_device: PydanticObjectId, ip_camera: str, user=Depends(get_user_info()), time_left_to_right: Optional[str] = None, time_right_to_left: Optional[str] = None,total_time: Optional[int] = None):
    return await event_service.get_count_image_by_ip_camera_from_crossline(id_company, id_device, ip_camera, user, time_left_to_right, time_right_to_left, total_time)

@router.get("/get-image-by-ip-camera-from-crossregion")
async def get_image_by_ip_camera_from_crossregion(id_company: PydanticObjectId, id_device: PydanticObjectId, ip_camera: str,
                                                user=Depends(get_user_info()), page: int = Query(0, ge=0), size: int = Query(10, gt=0),
                                                time_enter: Optional[str] = None, time_leave: Optional[str] = None,total_time: Optional[str] = None):
    return await event_service.get_image_by_ip_camera_from_crossregion(id_company, id_device, ip_camera, user, page, size, time_enter, time_leave, total_time)
@router.get("/get-count-image-by-ip-camera-from-crossregion")
async def get_count_image_by_ip_camera_from_crossregion(id_company: PydanticObjectId, id_device: PydanticObjectId, ip_camera: str, user=Depends(get_user_info()), time_enter: Optional[str] = None, time_leave: Optional[str] = None,total_time: Optional[str] = None):
    return await event_service.get_count_image_by_ip_camera_from_crossregion(id_company, id_device, ip_camera, user, time_enter, time_leave, total_time)