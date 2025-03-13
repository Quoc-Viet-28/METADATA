from datetime import datetime
from io import BytesIO

import requests
import cv2
import numpy as np
from bson import ObjectId

from app.constants.event_type_emum import EventTypeEnum
from app.services.event_dahua.event_handler.event_handler_box_ai_factory import EventHandlerBoxAIFactory
from app.models.camera_model import Camera
from app.services.event_dahua.image_helper import remap_coordinates, crop_image
from app.utils.image_processing import convert_BytesIO_to_webp
from app.utils.minio_utils import MinioServices
from app.models.event_model import Event


@EventHandlerBoxAIFactory.register_class(["CrossRegionDetection"])
class CrossRegionHandler:
    def __init__(self, type_name):
        self.type_name = type_name

    def get_name_image(self, name_file_iso):
        name_image_vehicle = f'{name_file_iso}_VEHICLE.WEBP'
        name_image_human = f'{name_file_iso}_HUMAN.WEBP'
        return name_image_vehicle, name_image_human

    async def get_ip_camera_by_channel_from_event(self, channel):
        camera = await Camera.find_one({"channel": int(channel)})
        return camera

    async def draw_region_on_image(self,coors,image_url, name_image):
        response = requests.get(image_url)
        if response.status_code != 200:
            raise ValueError(f"Không thể tải hình ảnh từ URL: {image_url}")
        image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
        image_width = image.shape[1]
        image_height = image.shape[0]
        coors=[(int(coor[0]), int(coor[1])) for coor in coors]
        coors=remap_coordinates(coors, 8192, image_width, image_height)
        if image is not None:
            points = np.array(coors, dtype=np.int32)
            points = points.reshape((-1, 1, 2))
            cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=2)
        _, buffer = cv2.imencode('.WEBP', image)
        data_img=BytesIO(buffer)
        minio_service = MinioServices()
        url = await minio_service.upload_file_from_bytesIO(data_img, name_image)
        return url

    async def handle_data_human(self, minio_service, data, image, name_file_iso, flow_1, flow_2):
        name_image_vehicle, name_image_human = self.get_name_image(name_file_iso)
        if data.get('Object', {}).get('BoundingBox', None) is not None and data.get('Object', {}).get('BoundingBox',None) != ['0','0','0','0']:
            human_img_crop = crop_image(image, data.get('Object', {}).get('BoundingBox', None))
            url_human = await minio_service.upload_file_from_bytesIO(human_img_crop, name_image_human, )
        else:
            url_human = None
        necessary_data = {
            'Event_ID': {
                f'Event_ID_{flow_1}': data.get('EventID', None),
                f'Event_ID_{flow_2}': None
            },
            'Object_Detect':
                {
                    'Human': {
                        f'Human_{flow_1}': {
                            'Object_ID': data.get('Object', {}).get('ObjectID', None),
                            'Human_BoundingBox': data.get('Object', {}).get('BoundingBox', None),
                        },
                        f'Human_{flow_2}': None
                    },
                    'Vehicle': None
                },
            'Time': {
                f'Time_{flow_1}': data.get('RealUTC', None),
                f'Time_{flow_2}': None,
                f'Total_Time': None
            },
            'Image_Vehicle_CrossRegion': None,
            'Image_Human_CrossRegion': {
                f'Image_Human_CrossRegion_{flow_1}': url_human,
                f'Image_Human_CrossRegion_{flow_2}': None
            },
        }
        return necessary_data
    async def handle_data_vehicle(self, minio_service, data, image, name_file_iso, flow_1, flow_2):
        name_image_vehicle, name_image_human = self.get_name_image(name_file_iso)
        if data.get('Object', {}).get('BoundingBox', None) is not None and data.get('Object', {}).get('BoundingBox',None) != ['0','0','0','0']:
            vehicle_img_crop = crop_image(image, data.get('Object', {}).get('BoundingBox', None))
            url_vehicle = await minio_service.upload_file_from_bytesIO(vehicle_img_crop, name_image_vehicle)
        else:
            url_vehicle = None
        necessary_data = {
            'Event_ID': {
                f'Event_ID_{flow_1}': data.get('EventID', None),
                f'Event_ID_{flow_2}': None
            },
            'Object_Detect':
                {
                    'Human': None,
                    'Vehicle': {
                        f'Vehicle_{flow_1}': {
                            'Object_ID': data.get('Object', {}).get('ObjectID', None),
                            'Vehicle_BoundingBox': data.get('Object', {}).get('BoundingBox', None),
                        },
                        f'Vehicle_{flow_2}': None
                    }
                },
            'Time': {
                f'Time_{flow_1}': data.get('RealUTC', None),
                f'Time_{flow_2}': None,
                f'Total_Time': None
            },
            'Image_Human_CrossRegion': None,
            'Image_Vehicle_CrossRegion': {
                f'Image_Vehicle_CrossRegion_{flow_1}': url_vehicle,
                f'Image_Vehicle_CrossRegion_{flow_2}': None
            },
        }
        return necessary_data
    async def combine_events(self, event1, event2):
        combined_data = {}
        all_keys = set(event1.data.keys()).union(set(event2.data.keys()))
        for key in all_keys:
            value1 = event1.data.get(key)
            value2 = event2.data.get(key)
            if isinstance(value2, list):
                value2 = [
                    {str(k): v for k, v in item.items()}
                    for item in value2 if isinstance(item, dict)
                ]
            if isinstance(value1, list):
                value1 = [
                    {str(k): v for k, v in item.items()}
                    for item in value1 if isinstance(item, dict)
                ]
            if key == 'Direction_Flow':
                combined_data[key] = [value1, value2] if value1 and value2 else value1 or value2
            elif key == "Time":
                time1 = value1.get(f"Time_{event1.data.get('Direction_Flow')}")
                time2 = value2.get(f"Time_{event2.data.get('Direction_Flow')}")
                time1 = int(time1) if time1 is not None else 0
                time2 = int(time2) if time2 is not None else 0
                combined_data[key] = {
                        f"Time_{event1.data.get('Direction_Flow')}": time1,
                        f"Time_{event2.data.get('Direction_Flow')}": time2,
                        "Total_Time": str(time2 - time1)
                }
            elif key == "Image":
                combined_data["Image"] = {
                    f"Image_{event1.data.get('Direction_Flow')}": value1.get(
                        f"Image_{event1.data.get('Direction_Flow')}"),
                    f"Image_{event2.data.get('Direction_Flow')}": value2.get(
                        f"Image_{event2.data.get('Direction_Flow')}")
                }
            elif key == "Image_Human_CrossRegion":
                if event1.data.get('Image_Human_CrossRegion', None) and event2.data.get('Image_Human_CrossRegion',
                                                                                          None) is not None:
                    combined_data["Image_Human_CrossRegion"] = {
                        f"Image_Human_CrossRegion_{event1.data.get('Direction_Flow')}": value1.get(
                            f"Image_Human_CrossRegion_{event1.data.get('Direction_Flow')}", None),
                        f"Image_Human_CrossRegion_{event2.data.get('Direction_Flow')}": value2.get(
                            f"Image_Human_CrossRegion_{event2.data.get('Direction_Flow')}", None)
                    }
                else:
                    combined_data["Image_Human_CrossRegion"] = None
            elif key == "Image_Vehicle_CrossRegion":
                if event1.data.get('Image_Vehicle_CrossRegion', None) and event2.data.get('Image_Vehicle_CrossRegion',
                                                                                      None) is not None:
                    combined_data["Image_Vehicle_CrossRegion"] = {
                        f"Image_Vehicle_CrossRegion_{event1.data.get('Direction_Flow')}": value1.get(
                            f"Image_Vehicle_CrossRegion_{event1.data.get('Direction_Flow')}", None),
                        f"Image_Vehicle_CrossRegion_{event2.data.get('Direction_Flow')}": value2.get(
                            f"Image_Vehicle_CrossRegion_{event2.data.get('Direction_Flow')}", None)
                    }
                else:
                    combined_data["Image_Vehicle_CrossRegion"] = None
            elif key == "Object_Detect":
                if event1.data.get('Object_Detect', {}).get('Human', None) is not None and event2.data.get(
                        'Object_Detect', {}).get('Human', None) is not None:
                    combined_data["Object_Detect"] = {
                        'Human': {
                            f"Human_{event1.data.get('Direction_Flow')}": value1.get('Human').get(
                                f"Human_{event1.data.get('Direction_Flow')}"),
                            f"Human_{event2.data.get('Direction_Flow')}": value2.get('Human').get(
                                f"Human_{event2.data.get('Direction_Flow')}")
                        },
                        'Vehicle': None
                    }
                elif event1.data.get('Object_Detect', {}).get('Vehicle', None) is not None and event2.data.get(
                        'Object_Detect', {}).get('Vehicle', None) is not None:
                    combined_data["Object_Detect"] = {
                        'Human': None,
                        'Vehicle': {
                            f"Vehicle_{event1.data.get('Direction_Flow')}": value1.get('Vehicle').get(
                                f"Vehicle_{event1.data.get('Direction_Flow')}"),
                            f"Vehicle_{event2.data.get('Direction_Flow')}": value2.get('Vehicle').get(
                                f"Vehicle_{event2.data.get('Direction_Flow')}")
                        }
                    }
            elif key == "Event_ID":
                combined_data["Event_ID"] = {
                    f"Event_ID_{event1.data.get('Direction_Flow')}": value1.get(f"Event_ID_{event1.data.get('Direction_Flow')}"),
                    f"Event_ID_{event2.data.get('Direction_Flow')}": value2.get(f"Event_ID_{event2.data.get('Direction_Flow')}")
                }
            else:
                if value1 == value2:
                    combined_data[key] = value1
                else:
                    combined_data[key] = [value1, value2] if value1 and value2 else value1 or value2
        return Event(
            event_type=event1.event_type,
            data=combined_data,
            company=event1.company,
            device=event1.device,
            camera=await self.get_ip_camera_by_channel_from_event(event1.data.get('Channel', None))
        )
    async def save(self, data, image, device):
        url_region = None
        data_save = None
        object_ID_current = data.get('Object', {}).get('ObjectID', None)
        name_event_current = data.get('EventBaseInfo', {}).get('Code', 'Unknown')
        minio_service = MinioServices()
        now = datetime.now().date()
        event_name = data.get('EventBaseInfo', {}).get('Code', 'Unknown')
        name_file_iso = f'{device.company.id}/{event_name}/{now}/{str(ObjectId())}'
        name_image = f'{name_file_iso}.WEBP'
        image_webp = await convert_BytesIO_to_webp(image)
        convert_image_webp_io = BytesIO(image_webp)
        url = await minio_service.upload_file_from_bytesIO(convert_image_webp_io, name_image)
        object_type = data.get('Object', {}).get('ObjectType', None)
        if data.get('DetectRegion', None) is not None:
            coors = data.get('DetectRegion', None)
            url_region = await self.draw_region_on_image(coors, url, name_image)
        flow_list = ['Enter', 'Leave']
        flow_1 = data.get('Direction', None)
        if flow_1 == flow_list[0]:
            flow_2 = flow_list[1]
        elif flow_1 == flow_list[1]:
            flow_2 = flow_list[0]
        else:
            flow_2 = None
        if object_type == 'Vehicle':
            data_save = await self.handle_data_vehicle(minio_service, data, image, name_file_iso, flow_1, flow_2)
        elif object_type == 'Human':
            data_save = await self.handle_data_human(minio_service, data, image, name_file_iso, flow_1, flow_2)
        data_share = {
            'Action': data.get('Action', None),
            'Channel': str(int(data.get('Channel', None))),
            'Detect_Region': data.get('DetectRegion', None),
            'Direction_Flow': data.get('Direction', None),
            'Name_Event': data.get('EventBaseInfo', {}).get('Code', 'Unknown'),
            'Image': {
                f'Image_{flow_1}': url_region,
                f'Image_{flow_2}': None
            },
            'is_combined': False
        }
        if data_save is not None:
            data_save.update(data_share)
        else:
            print("data_save is None. Cannot update.")
        new_event = Event(
            event_type=EventTypeEnum.CROSS_REGION,
            data=data_save,
            company=device.company,
            device=device,
            camera=await self.get_ip_camera_by_channel_from_event(data.get('Channel', None))
        )
        if object_ID_current and name_event_current:
            matching_event = await new_event.find_one(
                {f"data.Object_Detect.{object_type}.{object_type}_{flow_2}.Object_ID": object_ID_current,
                 "data.Name_Event": name_event_current, "data.is_combined": False, "data.Direction_Flow": {"$ne": flow_1}})
            if matching_event is None:
                await new_event.insert()
                print(f"Đã thêm new_event {new_event} vào MongoDB.")
                return new_event
            else:
                combined_event = await self.combine_events(matching_event, new_event)
                await combined_event.insert()
                print(f"Đã thêm combined_event {combined_event} vào MongoDB.")
                await matching_event.update({"$set": {"data.is_combined": True}})
                await combined_event.update({"$set": {"data.is_combined": True}})
                return combined_event
        else:
            await new_event.insert()
            print(f"Đã thêm {new_event} vào MongoDB.")
            return new_event