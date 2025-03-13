import re
from typing import Optional, Dict, Any

from beanie import PydanticObjectId
from pydantic import BaseModel, field_validator


class CameraCreate(BaseModel):
    name: str
    ip_camera: str
    httpPort: int
    user_name: str
    password: str
    rtsp: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[str] = None
    other_info: Dict[str, Any]
    id_ward: Optional[str] = None
    id_device: PydanticObjectId

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


class CameraUpdate(BaseModel):
    id: PydanticObjectId
    name: Optional[str] = None
    ip_camera: Optional[str] = None
    httpPort: Optional[int] = None
    user_name: Optional[str] = None
    password: Optional[str] = None
    rtsp: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[str] = None
    other_info: Optional[Dict[str, Any]] = None
    id_ward: Optional[str] = None

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

class GetRTSP(BaseModel):
    ip_camera: str
    port: int
    user_name: str
    password: str
