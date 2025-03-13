import asyncio
import re
from typing import Optional, Any

import unidecode
from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import HTTPException, status, Query

from app.constants.device_status_enum import DeviceStatusEnum
from app.constants.device_type_enum import DeviceTypeEnum, LIST_DEVICE_DAHUA
from app.core.security import check_role
from app.dto.device_dto import DeviceCreate, DeviceUpdate, DeviceUpdateStatus
from app.models.company_model import Company
from app.models.device_model import Device
from app.models.person_camera_model import PersonCamera
from app.models.person_model import Person
from app.models.ward_model import Ward
from app.services.event_dahua.dahua_event_service import DahuaEventThread
from app.utils.common_utils import get_company


class DeviceService:
    def __init__(self):
        self.dahua = DahuaEventThread()

    async def restart_listen(self, device_current: Device, device_old: Device):
        if device_old.device_type != device_current.device_type or device_old.ip_device != device_current.ip_device or \
                device_old.port != device_current.port or device_old.user_name != device_current.user_name or \
                device_old.password != device_current.password:
            print("restart_listen", device_current.id)
            self.dahua.remove_device(device_current.id)
            task = asyncio.create_task(self.dahua.add_device(device_current))
            self.dahua.active_tasks[device_current.id] = task

    async def create(self, device: DeviceCreate, user):
        company = await get_company(user, device.id_company)
        # device_exist = await Device.find_one( Device.company.id == company.id, Device.name == device.name)
        device_exist_name = await Device.find_one(Device.company.id == company.id, Device.name == device.name)
        if device_exist_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên thiết bị đã tồn tại"
            )
        device_exist_ip = await Device.find_one(Device.company.id == company.id, Device.ip_device == device.ip_device,
                                                Device.port == device.port)
        if device_exist_ip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Địa chỉ IP đã tồn tại"
            )
        ward = None

        if device.id_ward:
            ward = await Ward.get(device.id_ward)
            if not ward:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy xã/phường"
                )

        # Tạo một thiết bị mới với thông tin từ device
        new_device = Device(
            **device.dict(exclude={"id_company", "id_ward"}),  # Loại bỏ id_company
            company=company,  # Gán công ty cho thiết bị
            name_search=unidecode.unidecode(device.name).lower(),
            ward=ward

        )

        # Lưu thiết bị vào cơ sở dữ liệu
        await new_device.insert()
        task = asyncio.create_task(self.dahua.add_device(new_device))
        self.dahua.active_tasks[new_device.id] = task

        # Trả về thiết bị mới được tạo
        return new_device

    async def update(self, device_id: PydanticObjectId, device_data: DeviceUpdate, user):
        __check_role = check_role(user, "SYSTEM")
        if __check_role:
            device = await Device.get(device_id, fetch_links=True)
        else:
            if not user["company"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Không có quyền truy cập dữ liệu"
                )
            device = await Device.find_one(Device.id == device_id, Device.company.id == user["company"].id,
                                           fetch_links=True)
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thiết bị")

        # coppy device data
        device_old = device.copy()

        # check device name exist
        device_exist_name = await Device.find_one(Device.company.id == device.company.id,
                                                  Device.name == device_data.name,
                                                  Device.id != device_id)
        if device_exist_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên thiết bị đã tồn tại",
            )
        # check device ip exist
        device_exist_ip = await Device.find_one(
            Device.company.id == device.company.id,
            Device.ip_device == device_data.ip_device,
            Device.port == device_data.port,
            Device.id != device_id
        )

        if device_exist_ip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Địa chỉ IP đã tồn tại",
            )

        update_data = device_data.dict(exclude_unset=True, exclude={"id_company", "id_ward"})
        for field, value in update_data.items():
            setattr(device, field, value)

        if __check_role and device_data.id_company:
            company = await Company.get(device_data.id_company)
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy công ty"
                )
            device.company = company
        if device_data.name:
            device.name_search = unidecode.unidecode(device_data.name).lower()

        if device_data.id_ward:
            ward = await Ward.get(device_data.id_ward)
            if not ward:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy xã/phường"
                )
            device.ward = ward

        await device.replace()  # Automatically triggers `before_event` to update `updated_at`
        await self.restart_listen(device, device_old)

        return device

    async def get_by_id(self, device_id: PydanticObjectId):
        device = await Device.get(device_id, fetch_links=True)
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thiết bị")
        return device

    async def get_all(self, device_type: DeviceTypeEnum, page: int = Query(0, ge=0), size: int = Query(10, gt=0),
                      key_work: Optional[str] = Query(None),
                      is_full: bool = False, _status: Optional[str] = Query(None),
                      id_company: Optional[PydanticObjectId] = Query(None), user: Any = None):
        __check_role = check_role(user,"SYSTEM")

        if __check_role is False:
            if not user["company"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Không có quyền truy cập dữ liệu"
                )
            id_company = user["company"].id
        query = []
        if key_work:
            key_work = unidecode.unidecode(key_work).lower()
            regex = re.compile(f".*{key_work}.*", re.IGNORECASE)
            query.append({"name_search": {"$regex": regex}})
            query.append({"ip_device": {"$regex": regex}})

        if is_full:
            devices = await Device.find(Device.device_type == device_type, {} if not query else {"$or": query},
                                        Device.company.id == id_company,
                                        {"status": _status} if _status else {}, fetch_links=True
                                        ).sort("-created_at").to_list()
        else:
            devices = await Device.find(Device.device_type == device_type, {} if not query else {"$or": query},
                                        Device.company.id == id_company,
                                        {"status": _status} if _status else {}, fetch_links=True
                                        ).skip(page * size).limit(size).sort(
                "-created_at").to_list()
        print("tesdttttt: ",devices)
        print("comapppppny: ",user)
        return devices

    async def get_count(self, device_type: DeviceTypeEnum, key_work: Optional[str] = Query(None),
                        _status: Optional[str] = Query(None),
                        id_company: Optional[PydanticObjectId] = Query(None), user: Any = None):
        __check_role = check_role(user, "SYSTEM")
        if __check_role is False:
            if not user["company"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Không có quyền truy cập dữ liệu"
                )
            id_company = user["company"].id
        query = []
        if key_work:
            key_work = unidecode.unidecode(key_work).lower()
            regex = re.compile(f".*{key_work}.*", re.IGNORECASE)
            query.append({"name_search": {"$regex": regex}})
            query.append({"ip_device": {"$regex": regex}})

        count = await Device.find(Device.device_type == device_type, {} if not query else {"$or": query},
                                  Device.company.id == id_company,
                                  {"status": _status} if _status else {}
                                  ).count()

        return count

    async def set_status(self, device_id: PydanticObjectId, data: DeviceUpdateStatus, user):
        device = await Device.get(device_id, fetch_links=True)
        __check_role = check_role(user, "SYSTEM")
        if not __check_role:
            if not user["company"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Không có quyền truy cập dữ liệu"
                )
            if device.company.id != user["company"].id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Không có quyền truy cập dữ liệu"
                )
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thiết bị")
        device.status = data.status
        await device.replace()
        self.dahua.remove_device(device.id)
        if data.status == DeviceStatusEnum.STOP:
            await self.dahua.send_status_device(str(device.company.id), DeviceStatusEnum.STOP, device.id)
        if data.status == DeviceStatusEnum.START:
            task = asyncio.create_task(self.dahua.add_device(device))
            self.dahua.active_tasks[device.id] = task

        return device

    async def device_face(self, key_work: Optional[str] = Query(None), person=None):
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người này")

        query = []
        if key_work:
            key_work = unidecode.unidecode(key_work).lower()
            regex = re.compile(f".*{key_work}.*", re.IGNORECASE)
            query.append({"name_search": {"$regex": regex}})
            query.append({"ip_device": {"$regex": regex}})

        devices =  Device.find({
            "$and": [
                {
                    "company": {
                        "$ref": "Company",
                        "$id": person.company.id
                    }
                },
                {
                    "$or": [
                        {"device_type": DeviceTypeEnum.BOX_AI_DAHUA},
                        {"is_support_face": True}
                    ]
                }
            ]
        }, {} if not query else {"$or": query})
        return devices

    async def get_device_face(self, id_person: PydanticObjectId, page: int = Query(0, ge=0),
                              size: int = Query(10, gt=0),
                              key_work: Optional[str] = Query(None)):
        person = await Person.get(id_person, fetch_links=True)
        device_face = await self.device_face(key_work, person)
        devices = await device_face.skip(page * size).limit(size).sort(
            "-created_at").to_list()

        person_devices = await PersonCamera.find(PersonCamera.person.id == person.id, fetch_links=True).to_list()
        list_device = []
        for device in devices:
            list_device.append({
                "device": device,
                "is_activate": device.id in [person_device.device.id for person_device in person_devices]
            })
        return list_device

    async def get_count_device_face(self, id_person: PydanticObjectId, key_work: Optional[str] = Query(None)):
        person = await Person.get(id_person, fetch_links=True)
        device_face = await self.device_face(key_work, person)
        return await device_face.count()


device_service = DeviceService()
