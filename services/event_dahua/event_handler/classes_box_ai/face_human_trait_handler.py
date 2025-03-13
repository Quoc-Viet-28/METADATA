import json
from datetime import datetime
from io import BytesIO
from bson import ObjectId
from app.constants.event_data_enum import Beard_Human, Eye_Human, Glass_Human, Cap_Human, Mask_Human, Mouth_Human, \
    Bag_Human, CoatType_Human, HasBag_Human, HairStyle_Human, HasHat_Human, HasUmbrella_Human, RainCoat_Human, \
    DownClothes_Human
from app.constants.event_type_emum import EventTypeEnum
from app.services.event_dahua.event_handler.event_handler_box_ai_factory import EventHandlerBoxAIFactory
from app.models.camera_model import Camera
from app.services.event_dahua.image_helper import crop_image
from app.utils.image_processing import convert_BytesIO_to_webp
from app.utils.minio_utils import MinioServices
from app.models.event_model import Event

@EventHandlerBoxAIFactory.register_class(["HumanTrait"])
class HumanTraitHandler:
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
    async def handle_human_trait(self, minio_service, data, image, name_file_iso):
        url_face = None
        name_image = f'{name_file_iso}.WEBP'
        name_image_face = f'{name_file_iso}_FACE.WEBP'
        image_webp =await convert_BytesIO_to_webp(image)
        convert_image_webp_io = BytesIO(image_webp)
        url = await minio_service.upload_file_from_bytesIO(convert_image_webp_io, name_image)
        if data.get('FaceAttributes', {}).get('BoundingBox', None) is not None:
            face_img_crop = crop_image(image, data.get('FaceAttributes', {}).get('BoundingBox', None))
            # face_img_crop_webp = await convert_BytesIO_to_webp(face_img_crop.getvalue())
            # face_img_crop_webp_io = BytesIO(face_img_crop_webp)
            url_face = await minio_service.upload_file_from_bytesIO(face_img_crop, name_image_face)
        data_human_trait = {
            'Channel': str(int(data.get('Channel', None))),
            'Detect_Region': data.get('DetectRegion', None),
            'Name_Event': data.get('EventBaseInfo', {}).get('Code', None),
            'Event_ID': data.get('EventID', None),
            'Face_Attributes': {
                'Age': data.get('FaceAttributes', {}).get('Age', None),
                'Angle': data.get('FaceAttributes', {}).get('Angle', None),
                'Beard': self.to_enum(Beard_Human, data.get('FaceAttributes', {}).get('Beard', None)),
                'BoundingBox_Of_Face': data.get('FaceAttributes', {}).get('BoundingBox', None),
                'Emotion': data.get('FaceAttributes', {}).get('Emotion', None),
                'Eye': self.to_enum(Eye_Human, data.get('FaceAttributes', {}).get('Eye', None)),
                'Feature': data.get('FaceAttributes', {}).get('Feature', None),
                'Glass': self.to_enum(Glass_Human, data.get('FaceAttributes', {}).get('Glass', None)),
                'Hat': self.to_enum(Cap_Human, data.get('FaceAttributes', {}).get('Hat', None)),
                'Image': data.get('FaceAttributes', {}).get('Image', None),
                'Mask': self.to_enum(Mask_Human, data.get('FaceAttributes', {}).get('Mask', None)),
                'Mouth': self.to_enum(Mouth_Human, data.get('FaceAttributes', {}).get('Mouth', None)),
                'ObjectID_Of_Face': data.get('FaceAttributes', {}).get('ObjectID', None),
            },
            'Human_Attributes': {
                'Age': data.get('HumanAttributes', {}).get('Age', None),
                'BagType': self.to_enum(Bag_Human, data.get('HumanAttributes', {}).get('Bag', None)),
                'CoatType': self.to_enum(CoatType_Human, data.get('HumanAttributes', {}).get('CoatType', None)),
                'CoatColor': data.get('HumanAttributes', {}).get('CoatColor', None),
                'HairStyle': self.to_enum(HairStyle_Human, data.get('HumanAttributes', {}).get('HairStyle', None)),
                'Bag': self.to_enum(HasBag_Human, data.get('HumanAttributes', {}).get('HasBag', None)),
                'Hat': self.to_enum(HasHat_Human, data.get('HumanAttributes', {}).get('HasHat', None)),
                'Umbrella': self.to_enum(HasUmbrella_Human, data.get('HumanAttributes', {}).get('HasUmberlla', None)),
                'Mask': self.to_enum(Mask_Human, data.get('HumanAttributes', {}).get('Mask', None)),
                'RainCoat': self.to_enum(RainCoat_Human, data.get('HumanAttributes', {}).get('RainCoat', None)),
                'TrouserType': self.to_enum(DownClothes_Human,
                                            data.get('HumanAttributes', {}).get('TrousersType', None)),
                'TrouserColor': data.get('HumanAttributes', {}).get('TrousersColor', None),
            },
            'Time': data.get('RealUTC', None),
            'ObjectID_Of_Human': data.get('ObjectID', None),
            'Image': url,
            'Image_Face': url_face
        }
        return data_human_trait

    async def save(self,data, image,device):
        # with open(f'TEST_HUMAN.json', 'w') as f:
        #     json.dump(data, f, indent=4)
        minio_service = MinioServices()
        now = datetime.now().date()
        event_name = data.get('EventBaseInfo', {}).get('Code', 'Unknown')
        name_file_iso = f'{device.company.id}/{event_name}/{now}/{str(ObjectId())}'
        data_face_recognition = await self.handle_human_trait(minio_service, data, image, name_file_iso)
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
