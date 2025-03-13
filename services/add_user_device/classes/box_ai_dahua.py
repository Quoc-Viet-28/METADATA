from app.constants.device_type_enum import DeviceTypeEnum
from app.models.person_camera_model import PersonCamera
from app.services.add_user_device.BaseDevice import BaseDevice
from app.services.add_user_device.DeviceFactory import DeviceFactory
from app.services.event_dahua.text_helper import parse_text_data
from app.utils.api_dahua_utils import APIDahua
from app.utils.call_api_httpx import post_data, get_data


@DeviceFactory.register_class([DeviceTypeEnum.BOX_AI_DAHUA, DeviceTypeEnum.CAMERA_DAHUA_AI])
class BoxAIDahua(BaseDevice):
    apiDahua = APIDahua()

    async def create_person(self, person, device, content, group_id):
        url = f"{device.protocol}://{device.ip_device}:{device.port}/cgi-bin/faceRecognitionServer.cgi?action=addPerson&" \
              f"groupID={group_id}&name={person.name}&sex={person.sex.value}&id={str(person.id)}"
        text_response = await post_data(url, device.user_name, device.password, content)
        print("Create person", text_response)
        if text_response.status_code != 200:
            print("Error create person", text_response.text)
            return None
        uid = parse_text_data(text_response.text)
        return uid

    async def create(self, device, person, group_id=None):
        try:
            if not group_id:
                is_deploy = False
                if self.type_name == DeviceTypeEnum.CAMERA_DAHUA_AI:
                    is_deploy = True
                group_id = await self.apiDahua.check_group_and_create(device.protocol, device.ip_device, device.port,
                                                                      device.user_name,
                                                                      device.password, is_deploy=is_deploy)

            image = await get_data(person.image, None, None)
            if image.status_code != 200:
                print("Error get image")
                return False, "Lỗi lấy ảnh của người dùng"

            uid = await self.create_person(person, device, image.content, group_id)
            person = PersonCamera(device=device, person=person, person_device_id=str(person.id),
                                  other_info={"uid": uid.get("uid"), "group_id": group_id})
            await person.insert()
            return True, person

        except Exception as e:
            print(e)
            return False, str(e)

    async def create_person_existed(self, device, person, person_camera, group_id=None):
        try:
            if not group_id:
                group_id = await self.apiDahua.check_group_and_create(device.protocol, device.ip_device, device.port,
                                                                      device.user_name,
                                                                      device.password)

            data = await self.apiDahua.check_person_existed(device.protocol, device.ip_device, device.port,
                                                            device.user_name,
                                                            device.password, group_id, str(person.id))
            if data and data.get("totalCount") and int(data.get("totalCount")) == 0:
                await person_camera.delete()
                _is, _data = await self.create(device, person, group_id)
                return _is, _data

            return False, "Người này đã tồn tại trên thiết bị"

        except Exception as e:
            print(e)
            return False, str(e)

    async def delete_person(self, person_camera, device, person):
        try:
            uid = person_camera.other_info.get("uid")
            group_id = person_camera.other_info.get("group_id")
            url = f"{device.protocol}://{device.ip_device}:{device.port}/cgi-bin/faceRecognitionServer.cgi?action=deletePerson&uid={uid}&groupID={group_id}"

            text_response = await get_data(url, device.user_name, device.password)
            if text_response.status_code != 200:
                print("Error delete person", text_response.text)
                return False, "Lỗi xóa người dùng"
            return True, "Xóa người dùng thành công"
        except Exception as e:
            print(e)
            return False, str(e)

    async def update(self, person_camera, is_update_image=False):
        try:
            device = person_camera.device
            person = person_camera.person
            uid = person_camera.other_info.get("uid")
            group_id = person_camera.other_info.get("group_id")
            url = f"{device.protocol}://{device.ip_device}:{device.port}/cgi-bin/faceRecognitionServer.cgi?action=modifyPerson&" \
                  f"uid={uid}&groupID={group_id}&name={person.name}&sex={person.sex.value}"
            content = None
            if is_update_image:
                image = await get_data(person.image, None, None)
                if image.status_code != 200:
                    print("Error get image")
                    return False, "Lỗi lấy ảnh của người dùng"
                content = image.content

            text_response = await post_data(url, device.user_name, device.password, content)
            if text_response.status_code != 200:
                print("Error create person", text_response.text)
                return False, "Lỗi cập nhật người dùng"
            uid = parse_text_data(text_response.text)
            return True, uid
        except Exception as e:
            return False, str(e)
