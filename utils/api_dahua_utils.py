import json

from app.services.event_dahua.text_helper import parse_text_data
from app.utils.call_api_httpx import get_data, post_data


class APIDahua(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(APIDahua, cls).__new__(cls)
        return cls.instance

    async def find_group(self, protocol, ip_device, port, user_name, password):
        try:
            url = f"{protocol}://{ip_device}:{port}/cgi-bin/faceRecognitionServer.cgi?action=findGroup"
            response = await get_data(url, user_name, password)
            if response.status_code != 200:
                return None
            return parse_text_data(response.text)
        except Exception as e:
            return None

    async def create_face_group(self, protocol, ip_device, port, user_name, password, group_name, group_detail):
        try:
            url = f"{protocol}://{ip_device}:{port}/cgi-bin/faceRecognitionServer.cgi?action=createGroup&groupName={group_name}&groupDetail={group_detail}"
            response = await get_data(url, user_name, password)
            if response.status_code != 200:
                return None
            return parse_text_data(response.text)
        except Exception as e:
            return None

    async def deloy_group(self, protocol, ip_device, port, user_name, password, groupID, channel=1):
        try:
            url = f"{protocol}://{ip_device}:{port}/cgi-bin/faceRecognitionServer.cgi?action=putDisposition&groupID={groupID}&list[0].channel={channel}&list[0].similary=80"
            response = await get_data(url, user_name, password)
            if response.status_code != 200:
                return None
            return parse_text_data(response.text)
        except Exception as e:
            return None

    async def check_group_and_create(self, protocol, ip_device, port, user_name, password, is_deploy=False):
        groups = await self.find_group(protocol, ip_device, port, user_name, password)
        if not groups or not groups.get("GroupList"):
            return None
        group_id = None
        for group in groups.get("GroupList"):
            if group.get("groupName") == "ORYZA_METADATA":
                group_id = group.get("groupID")
                break

        if not group_id:
            group = await self.create_face_group(protocol, ip_device, port, user_name, password, "ORYZA_METADATA",
                                                 "ORYZA_METADATA")
            if not group or not group.get("groupID"):
                print("check_group_and_create Error create group")
                return None
            group_id = group.get("groupID")
            if is_deploy:
                await self.deloy_group(protocol, ip_device, port, user_name, password, group_id)
            return group_id
        return group_id

    async def check_person_existed(self, protocol, ip_device, port, user_name, password, groupID, person_id):
        try:
            url = f"{protocol}://{ip_device}:{port}/cgi-bin/faceRecognitionServer.cgi?action=startFind&condition.GroupID[0]={groupID}&person.ID={person_id}"
            response = await get_data(url, user_name, password)
            if response.status_code != 200:
                return None
            return parse_text_data(response.text)
        except Exception as e:
            return None

    async def get_camera(self, protocol, ip_device, port, user_name, password):
        try:
            url = f"{protocol}://{ip_device}:{port}/cgi-bin/LogicDeviceManager.cgi?action=getCameraAll"
            response = await get_data(url, user_name, password)
            if response.status_code != 200:
                return None
            return parse_text_data(response.text).get("camera")
        except Exception as e:
            return None

    async def get_state_camera(self, protocol, ip_device, port, user_name, password):
        try:
            url = f"{protocol}://{ip_device}:{port}/cgi-bin/api/LogicDeviceManager/getCameraState"
            payload = json.dumps({
                "uniqueChannels": [
                    -1
                ]
            })
            response = await post_data(url, user_name, password, payload)
            if response.status_code != 200:
                return None
            return response.json().get("states")
        except Exception as e:
            print(e)
            return None

    async def create_camera(self, device, camera, channel):
        try:

            url = f"{device.protocol}://{device.ip_device}:{device.port}/cgi-bin/LogicDeviceManager.cgi?action=addCameraByGroup"

            payload = json.dumps({
                "group": [
                    {
                        "DeviceInfo": {
                            "UserName": camera.user_name,
                            "Password": camera.password,
                            "ProtocolType": "Private",
                            "Port": camera.httpPort,
                            "Address": camera.ip_camera,
                        },
                        "cameras": [
                            {
                                "uniqueChannel": channel + 1
                            }
                        ]
                    }
                ]
            })
            response = await post_data(url, device.user_name, device.password, payload)

            return response.text
        except Exception as e:
            print("error", e)
            return None
