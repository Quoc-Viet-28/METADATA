import re
from typing import Optional, Dict, Any

from beanie import PydanticObjectId
from pydantic import BaseModel, constr, validator, field_validator

from app.constants.device_status_enum import DeviceStatusEnum
from app.constants.device_type_enum import DeviceTypeEnum


class DeviceCreate(BaseModel):
    name: str
    device_type: DeviceTypeEnum
    ip_device: str
    port: int
    user_name: str
    password: str
    rtsp: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[str] = None
    id_ward: Optional[str] = None
    other_info: Dict[str, Any]
    id_company: Optional[PydanticObjectId] = None
    is_support_face: Optional[bool] = False

    @field_validator('coordinates')
    def validate_coordinates(cls, v):
        coordinate_regex = r"^([-+]?\d{1,2}(?:\.\d+)?),\s*([-+]?\d{1,3}(?:\.\d+)?)$"
        match = re.match(coordinate_regex, v)
        if not match:
            raise ValueError('Coordinates must be in the format "latitude, longitude"')

        lat, lon = map(float, v.split(','))
        if not (-90 <= lat <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        if not (-180 <= lon <= 180):
            raise ValueError('Longitude must be between -180 and 180')

        return v


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    device_type: Optional[DeviceTypeEnum] = None
    ip_device: Optional[str] = None
    port: Optional[int] = None
    user_name: Optional[str] = None
    password: Optional[str] = None
    rtsp: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[str] = None
    other_info: Optional[Dict[str, Any]] = None
    id_company: Optional[PydanticObjectId] = None
    id_ward: Optional[str] = None
    is_support_face: Optional[bool] = None

    @field_validator('coordinates')
    def validate_coordinates(cls, v):
        coordinate_regex = r"^([-+]?\d{1,2}(?:\.\d+)?),\s*([-+]?\d{1,3}(?:\.\d+)?)$"
        match = re.match(coordinate_regex, v)
        if not match:
            raise ValueError('Coordinates must be in the format "latitude, longitude"')

        lat, lon = map(float, v.split(','))
        if not (-90 <= lat <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        if not (-180 <= lon <= 180):
            raise ValueError('Longitude must be between -180 and 180')

        return v


class DeviceUpdateStatus(BaseModel):
    status: DeviceStatusEnum
