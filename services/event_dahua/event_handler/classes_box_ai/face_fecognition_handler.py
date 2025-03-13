from datetime import datetime
from io import BytesIO

from bson import ObjectId
from app.models.event_model import Event

from app.constants.event_type_emum import EventTypeEnum
from app.services.event_dahua.event_handler.event_handler_box_ai_factory import EventHandlerBoxAIFactory
from app.models.camera_model import Camera
from app.constants.event_data_enum import (Beard_Human, Eye_Human, Glass_Human, Mask_Human, Mouth_Human, HasHat_Human)
from app.services.event_dahua.image_helper import crop_image
from app.utils.image_processing import convert_BytesIO_to_webp
from app.utils.minio_utils import MinioServices


@EventHandlerBoxAIFactory.register_class(["FaceRecognition"])
class FaceRecognitionHandler:
    def __init__(self, type_name):
        self.type_name = type_name

    def to_enum(self, enum_class, value):
        try:
            return str(enum_class(value).name)
        except ValueError:
            return None

    async def get_ip_camera_by_channel_from_event(self, channel):
        camera = await Camera.find_one({"channel": int(channel)})
        return camera

    async def handle_face_recognition(self, minio_service, data, image, name_file_iso):
        url_face = None
        candidates_data = None
        name_image_big = f'{name_file_iso}.WEBP'
        name_image_face = f'{name_file_iso}_FACE.WEBP'
        image_webp = await convert_BytesIO_to_webp(image)
        convert_image_webp_io = BytesIO(image_webp)
        url = await minio_service.upload_file_from_bytesIO(convert_image_webp_io, name_image_big)
        if data.get('Face', {}).get('BoundingBox', None) is not None:
            face_img_crop = crop_image(image, data.get('Face', {}).get('BoundingBox', None))
            # face_img_crop_webp = await convert_BytesIO_to_webp(face_img_crop.getvalue())
            # face_img_crop_webp_io = BytesIO(face_img_crop_webp)
            url_face = await minio_service.upload_file_from_bytesIO(face_img_crop, name_image_face)
        if data.get('Candidates', None) is not None:
            candidates_data = {
                'Name': data['Candidates'][0]['Person']['Name'],
                'Birthday': data['Candidates'][0]['Person']['Birthday'],
                'CertificateType': data['Candidates'][0]['Person']['CertificateType'],
                'City': data['Candidates'][0]['Person']['City'],
                'Country': data['Candidates'][0]['Person']['Country'],
                'Database': data['Candidates'][0]['Person']['GroupName'],
                'HomeAddress': data['Candidates'][0]['Person']['HomeAddress'],
                'ID_Card': data['Candidates'][0]['Person']['ID'],
                'Similarity': data['Candidates'][0]['Similarity']
            }
        shared_data = {
            'Channel': str(int(data.get('Channel', None)) + 1),
            'Class': data.get('Class', None),
            'Name_Event': data.get('Code', None),
            'Age': data.get('Face', {}).get('Age', None),
            'Beard': self.to_enum(Beard_Human, data.get('Face', {}).get('Beard', None)),
            'BoundingBox': data.get('Face', {}).get('BoundingBox', None),
            'Eye': self.to_enum(Eye_Human, data.get('Face', {}).get('Eye', None)),
            'Feature': data.get('Face', {}).get('Feature', None),
            'Glass': self.to_enum(Glass_Human, data.get('Face', {}).get('Glass', None)),
            'Mask': self.to_enum(Mask_Human, data.get('Face', {}).get('Mask', None)),
            'Mouth': self.to_enum(Mouth_Human, data.get('Face', {}).get('Mouth', None)),
            'Sex': data.get('Face', {}).get('Sex', None),
            'Hat': self.to_enum(HasHat_Human, data.get('Object', {}).get('Hat', None)),
            'Time': data.get('RealUTC', None),
            'Candidates': candidates_data,
            'Image': url,
            'Image_Face': url_face
        }
        return shared_data

    async def save(self, data, image,device):
        minio_service = MinioServices()
        now = datetime.now().date()
        event_name = data.get('EventBaseInfo', {}).get('Code', 'Unknown')
        name_file_iso = f'{device.company.id}/{event_name}/{now}/{str(ObjectId())}'
        data_face_recognition = await self.handle_face_recognition(minio_service, data, image, name_file_iso)
        new_event = Event(
            event_type=EventTypeEnum.FACE,
            data=data_face_recognition,
            company=device.company,
            device=device,
            camera = await self.get_ip_camera_by_channel_from_event(data.get('Channel', None))
        )
        await new_event.insert()
        print(f"Đã thêm {new_event} vào MongoDB.")
        return new_event