import unidecode
from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.dto.camera_dto import CameraCreate, CameraUpdate
from app.models.camera_model import Camera
from app.models.device_model import Device
from app.models.ward_model import Ward
from app.utils.api_dahua_utils import APIDahua


class CameraService:

    async def create(self, request: CameraCreate):
        apiDahua = APIDahua()
        device = await Device.get(request.id_device)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thiết bị"
            )
        ward = None
        if request.id_ward:
            ward = await Ward.get(request.id_ward)
            if not ward:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy xã/phường"
                )
        channels = await self.get_channel_empty(device=device)
        if len(channels) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy kênh trống"
            )

        camera_device = await apiDahua.create_camera(device, request, channels[0])
        if not camera_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không thể tạo camera"
            )
        rtsp = f"rtsp://{device.user_name}:{device.password}@{device.ip_device}/cam/realmonitor?channel={channels[0]}&subtype=0"

        camera = Camera(**request.dict(exclude={"id_device", "id_ward"}),
                        name_search=unidecode.unidecode(request.name).lower(),
                        ward=ward, device=device, status="Unconnect", channel=channels[0])
        camera.rtsp = rtsp
        await camera.insert()
        return camera

    async def update(self, request: CameraUpdate):
        camera = await Camera.get(request.id, fetch_links=True)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy camera"
            )
        if request.id_ward:
            ward = await Ward.get(request.id_ward)
            if not ward:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy xã/phường"
                )
            camera.ward = ward

        update_data = request.dict(exclude_unset=True, exclude={"id_ward"})
        for field, value in update_data.items():
            setattr(camera, field, value)
        if request.ip_camera or request.httpPort or request.user_name or request.password:
            apiDahua = APIDahua()
            camera_device = await apiDahua.create_camera(camera.device, camera, camera.channel)
            if not camera_device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không thể cập nhật camera"
                )

        camera.name_search = unidecode.unidecode(camera.name).lower()

        await camera.replace()
        return camera

    async def delete(self, camera_id: PydanticObjectId):
        camera = await Camera.get(camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy camera"
            )

        await camera.delete()
        return "Xóa camera thành công"

    async def sync_camera(self, device_id: PydanticObjectId = None):
        device = await Device.get(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thiết bị"
            )
        apiDahua = APIDahua()
        cameras = await apiDahua.get_camera(device.protocol, device.ip_device, device.port, device.user_name,
                                            device.password)

        for i in range(0, len(cameras)):
            camera = cameras[i]
            deviceInfo = camera.get("DeviceInfo")
            channel = i
            camera_exist = await Camera.find_one(
                {"channel": channel, "device": {"$ref": "Device", "$id": device_id}})
            if camera.get("Enable") == "true":
                if deviceInfo is not None:
                    name = deviceInfo.get("Name")
                    name_search = unidecode.unidecode(name).lower()
                    ip_camera = deviceInfo.get("Address")
                    httpPort = deviceInfo.get("HttpPort")
                    user_name = deviceInfo.get("UserName")
                    rtsp = f"rtsp://{device.user_name}:{device.password}@{device.ip_device}/cam/realmonitor?channel={channel + 1}&subtype=0"
                    if camera_exist:
                        camera_exist.ip_camera = ip_camera
                        camera_exist.httpPort = httpPort
                        camera_exist.user_name = user_name
                        camera_exist.other_info = {"name": name}
                        camera_exist.rtsp = rtsp

                        await camera_exist.replace()
                    else:
                        cam = Camera(name=name, name_search=name_search, ip_camera=ip_camera, httpPort=httpPort,
                                     user_name=user_name, password="", rtsp=rtsp, address="", coordinates="",
                                     other_info={"name": name},
                                     ward=None, device=device, channel=channel, status="Unconnect")
                        await cam.insert()
            else:
                if camera_exist:
                    await camera_exist.delete()

        return "Đồng bộ camera thành công"

    async def get_camera_by_device(self, device_id: PydanticObjectId):
        apiDahua = APIDahua()
        device = await Device.get(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thiết bị"
            )
        cameras = await Camera.find({"device": {"$ref": "Device", "$id": device_id}}).to_list()
        channels = await apiDahua.get_state_camera(device.protocol, device.ip_device, device.port, device.user_name,
                                                   device.password)
        data_result = []
        for channel in channels:
            for camera in cameras:
                if camera.channel == channel.get("channel"):
                    camera.status = channel.get("connectionState")
                    data_result.append(camera)
                    break

        return data_result

    async def get_channel_empty(self, device_id: PydanticObjectId = None, device=None):
        if not device:
            device = await Device.get(device_id)
            if not device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy thiết bị"
                )
        apiDahua = APIDahua()
        channels = await apiDahua.get_state_camera(device.protocol, device.ip_device, device.port, device.user_name,
                                                   device.password)
        if not channels:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy kênh"
            )
        list_channel = []
        for i in range(0, len(channels)):
            if channels[i].get("connectionState") == "Empty":
                list_channel.append(channels[i].get("channel"))
        return list_channel


camera_service = CameraService()
