import asyncio
import time

from fastapi import HTTPException, status

from app.constants.device_type_enum import DeviceTypeEnum
from app.dto.person_camera_dto import PersonCameraCreateMutil, PersonCameraCreate, ManyPersonCameraCreateMutil
from app.models.device_model import Device
from app.models.person_camera_model import PersonCamera
from app.models.person_model import Person
from app.services.add_user_device.DeviceFactory import DeviceFactory
from app.utils.api_dahua_utils import APIDahua
from app.websocket.ConnectionProcessPersonManager import connection_process_person_manager


class PersonCameraService:
    list_person_camera = {}
    apiDahua = APIDahua()
    list_check_person = []

    async def check_person_in_camera(self, id_person):
        if str(id_person) in self.list_check_person:
            return True
        return False

    async def add_one_person_to_all_camera(self, id_person):
        person = await Person.find_one({"_id": id_person}, fetch_links=True)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người này"
            )
        self.list_check_person.append(str(person.id))

        devices = await Device.find({
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
        }).sort("-created_at").to_list()
        list_device_error = []
        list_device_success = []
        for device in devices:
            try:
                await self.add_user_to_device(request=None, person=person, device=device)
                list_device_success.append(device.name)
            except Exception as e:
                print(e)
                list_device_error.append({
                    "device": device.name,
                    "error": str(e)
                })
        # remove person from list check
        self.list_check_person.remove(str(person.id))
        await connection_process_person_manager.send_message_json([str(id_person)], {
            "status": "success",
            "type": "add_one_person_to_all_camera",
            "message": "Thêm người vào tất cả camera hoàn tất",
            "id_person": str(id_person)
        })
        return {
            "success": list_device_success,
            "error": list_device_error
        }

    async def add_many_person_to_one_device(self, request: ManyPersonCameraCreateMutil):
        device = await Device.find_one({"_id": request.id_device}, fetch_links=True)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thiết bị này"
            )

        persons = await Person.find({
            "company": {
                "$ref": "Company",
                "$id": device.company.id
            }

        }).to_list()
        list_person_error = []
        list_person_success = []
        group_id = None
        if device.device_type == DeviceTypeEnum.BOX_AI_DAHUA:
            group_id = await self.apiDahua.check_group_and_create(device.protocol, device.ip_device, device.port,
                                                                  device.user_name,
                                                                  device.password)
        if not group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tạo được group"
            )
        for person in persons:
            try:
                await self.add_user_to_device(request=None, person=person, device=device, group_id=group_id)
                list_person_success.append(person.name)
            except Exception as e:
                list_person_error.append({
                    "person": person.name,
                    "error": str(e)
                })
        await connection_process_person_manager.send_message_json([str(request.id_device)], {
            "status": "success",
            "type": "add_many_person_to_one_device",
            "message": "Thêm tất cả đối tượng vào  camera hoàn tất",
            "id_person": str(request.id_device)
        })
        return {
            "success": list_person_success,
            "error": list_person_error
        }

    async def add_user_to_device(self, request: PersonCameraCreate = None, person: Person = None,
                                 device: Device = None, group_id=None):
        """
            - Tránh trường hợp thêm 1 người cùng lúc vào 1 thiết bị
        """
        id_person = request.id_person if request else person.id
        id_device = request.id_device if request else device.id
        if id_person in self.list_person_camera and \
                self.list_person_camera[id_person] == id_device:
            await connection_process_person_manager.send_message_json([str(id_person), str(id_device)], {
                "status": "error",
                "type": "add",
                "message": "Người này đang được thêm vào thiết bị",
                "id_device": str(id_device),
                "id_person": str(id_person)
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người này đang được thêm vào thiết bị"
            )
        self.list_person_camera[id_person] = id_device
        # ---------------------------------------------------------------------------------------

        try:
            check = False
            if not person:
                person = await Person.find_one({"_id": request.id_person}, fetch_links=True)
                check = True
            if not device:
                device = await Device.find_one({"_id": request.id_device}, fetch_links=True)

            if not person:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy người này"
                )
            if not device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy thiết bị này"
                )

            if check:
                if person.company.id != device.company.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Thiết bị và người này không cùng công ty"
                    )

            person_camera = await PersonCamera.find_one({
                "person": {
                    "$ref": "Person",
                    "$id": person.id
                },
                "device": {
                    "$ref": "Device",
                    "$id": device.id
                }
            })
            deviceFactory = DeviceFactory.add_class(device.device_type)

            """
             - Nêu người này đã tồn tại trên thiết bị thì sủ dụng hàm create_person_existed
             - Mặc định nếu device không override hàm create_person_existed thì sẽ báo ~Người này đã tồn tại trên thiết bị~
            """
            if person_camera:
                _is_sus, _data = await deviceFactory.create_person_existed(device=device, person=person,
                                                                           person_camera=person_camera,
                                                                           group_id=group_id)
                if not _is_sus:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=_data
                    )
                await connection_process_person_manager.send_message_json([str(id_person), str(id_device)], {
                    "status": "success",
                    "type": "add",
                    "message": "Thêm người thành công",
                    "id_device": str(id_device),
                    "id_person": str(id_person),
                })

                return _data
            # ----------------------------------------------------------------------------------------------------------
            """ 
                - Nếu người này chưa tồn tại trên thiết bị thì sử dụng hàm create
            """
            is_sus, data = await deviceFactory.create(device=device, person=person, group_id=group_id)
            if not is_sus:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=data
                )
            await connection_process_person_manager.send_message_json([str(id_person), str(id_device)], {
                "status": "success",
                "type": "add",
                "message": "Thêm người thành công",
                "id_device": str(id_device),
                "id_person": str(id_person),
            })
            return data

        except Exception as e:
            error_message = str(e).replace("400:", "").strip()
            error_message = error_message.replace("404:", "").strip()
            await connection_process_person_manager.send_message_json([str(id_person), str(id_device)], {
                "status": "error",
                "type": "add",
                "message": "Thêm người thất bại",
                "id_device": str(id_device),
                "id_person": str(id_person)
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        finally:
            if id_person in self.list_person_camera:
                del self.list_person_camera[id_person]

    async def delete_user_from_device(self, request: PersonCameraCreate = None, person: Person = None,
                                      device: Device = None):
        """
            - Tránh trường hợp thao tác xóa 1 người cùng lúc trên 1 thiết bị
        """
        id_person = request.id_person if request else person.id
        id_device = request.id_device if request else device.id
        if id_person in self.list_person_camera and \
                self.list_person_camera[id_person] == id_device:
            await connection_process_person_manager.send_message_json([str(id_person), str(id_device)], {
                "status": "error",
                "type": "delete",
                "message": "Người này đang được xóa khỏi thiết bị",
                "id_device": str(id_device),
                "id_person": str(id_person)
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người này đang được xóa khỏi thiết bị"
            )
        self.list_person_camera[id_person] = id_device
        # ---------------------------------------------------------------------------------------

        try:
            check = False
            if not person:
                person = await Person.find_one({"_id": request.id_person}, fetch_links=True)
                check = True
            if not device:
                device = await Device.find_one({"_id": request.id_device}, fetch_links=True)

            if not person:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy người này"
                )
            if not device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy thiết bị này"
                )

            if check:
                if person.company.id != device.company.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Thiết bị và người này không cùng công ty"
                    )

            person_camera = await PersonCamera.find_one({
                "person": {
                    "$ref": "Person",
                    "$id": person.id
                },
                "device": {
                    "$ref": "Device",
                    "$id": device.id
                }
            })
            deviceFactory = DeviceFactory.add_class(device.device_type)
            if not person_camera:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Người này không tồn tại trên thiết bị"
                )

            is_sus, data = await deviceFactory.delete_person(person_camera=person_camera, device=device, person=person)
            await person_camera.delete()
            await connection_process_person_manager.send_message_json([str(id_person), str(id_device)], {
                "status": "success",
                "type": "delete",
                "message": "Xóa người thành công",
                "id_device": str(id_device),
                "id_person": str(id_person)
            })
            return "Xóa người thành công"

        except Exception as e:
            error_message = str(e).replace("400:", "").strip()
            error_message = error_message.replace("404:", "").strip()
            await connection_process_person_manager.send_message_json([str(id_person), str(id_device)], {
                "status": "error",
                "type": "delete",
                "message": "Xóa người thất bại",
                "id_device": str(id_device),
                "id_person": str(id_person)
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        finally:
            if id_person in self.list_person_camera:
                del self.list_person_camera[id_person]

    async def delete_one_person_from_all_camera(self, request: PersonCameraCreateMutil):
        person = await Person.find_one({"_id": request.id_person}, fetch_links=True)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người này"
            )
        self.list_check_person.append(str(person.id))

        person_cameras = await PersonCamera.find(PersonCamera.person.id == person.id, fetch_links=True).sort("-created_at").to_list()
        list_device_error = []
        list_device_success = []
        for person_camera in person_cameras:
            device = person_camera.device

            try:
                await self.delete_user_from_device(request=None, person=person, device=device)
                list_device_success.append(device.name)
            except Exception as e:
                list_device_error.append({
                    "device": device.name,
                    "error": str(e)
                })
        # remove person from list check
        self.list_check_person.remove(str(person.id))

        await connection_process_person_manager.send_message_json([str(request.id_person)], {
            "status": "success",
            "type": "delete_one_person_from_all_camera",
            "message": "Xóa người khỏi tất cả camera hoàn tất",
            "id_person": str(request.id_person)
        })

        return {
            "success": list_device_success,
            "error": list_device_error
        }

    async def delete_many_person_from_one_device(self, request: ManyPersonCameraCreateMutil):
        device = await Device.find_one({"_id": request.id_device}, fetch_links=True)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thiết bị này"
            )

        personCameras = await PersonCamera.find(PersonCamera.device.id == device.id, fetch_links=True).to_list()

        list_person_error = []
        list_person_success = []
        for personCamera in personCameras:
            person = personCamera.person
            try:
                await self.delete_user_from_device(request=None, person=person, device=device)
                list_person_success.append(person.name)
            except Exception as e:
                list_person_error.append({
                    "person": person.name,
                    "error": str(e)
                })

        await connection_process_person_manager.send_message_json([str(request.id_device)], {
            "status": "success",
            "type": "delete_many_person_from_one_device",
            "message": "Xóa tất cả đối tượng khỏi camera hoàn tất",
            "id_person": str(request.id_device)
        })
        return {
            "success": list_person_success,
            "error": list_person_error
        }

    async def update_person_camera(self, person: Person, is_update_image=False):
        person_cameras = await PersonCamera.find(PersonCamera.person.id == person.id, fetch_links=True).to_list()
        for person_camera in person_cameras:
            device = person_camera.device
            deviceFactory = DeviceFactory.add_class(device.device_type)
            await deviceFactory.update(person_camera=person_camera, is_update_image=is_update_image)


person_camera_services = PersonCameraService()
