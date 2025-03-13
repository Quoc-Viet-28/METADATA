import json
from datetime import datetime
from io import BytesIO
from bson import ObjectId
from app.constants.event_data_enum import Beard_Human, Glass_Human, Cap_Human, Eye_Human, Mask_Human, Mouth_Human, \
    HasBag_Human, CarrierBag_Human, DownClothes_Human, Helmet_Human, Umbrella_Human, HairStyle_Human, RainCoat_Human, \
    UpClothes_Human
from app.constants.event_type_emum import EventTypeEnum
from app.services.event_dahua.event_handler.event_handler_box_ai_factory import EventHandlerBoxAIFactory
from app.models.camera_model import Camera
from app.services.event_dahua.image_helper import crop_image, crop_image_original
from app.utils.image_processing import convert_BytesIO_to_webp
from app.utils.minio_utils import MinioServices
from app.models.event_model import Event


@EventHandlerBoxAIFactory.register_class(["TrafficJunction"])
class TrafficJunctionHandler:
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

    def get_name_image(self, name_file_iso):
        name_image_plate = f'{name_file_iso}_PLATE.WEBP'
        name_image_vehicle = f'{name_file_iso}_VEHICLE.WEBP'
        return name_image_plate, name_image_vehicle

    async def handle_data_motor(self,minio_service, data, image, name_file_iso):
        url_plate = None
        url_vehicle = None
        name_image_plate, name_image_vehicle = self.get_name_image(name_file_iso)
        object_data = data.get('Object', {})
        vehicle_data = data.get('Vehicle', {})
        traffic_data = data.get('TrafficCar', {})
        name_image_plate = f'{name_file_iso}_PLATE.WEBP'
        if object_data.get('Text', None) is not None and object_data.get('Text', None) != '':
            if object_data.get('BoundingBox') is not None and object_data.get('BoundingBox') != ['0', '0', '0', '0']:
                plate_crop_image = crop_image(image, object_data.get('BoundingBox'))
                # plate_crop_image_webp = await convert_BytesIO_to_webp(plate_crop_image.getvalue())
                # plate_crop_image_webp_io = BytesIO(plate_crop_image_webp)
                url_plate = await minio_service.upload_file_from_bytesIO(plate_crop_image, name_image_plate)
        if vehicle_data.get('BoundingBox', None) is not None and vehicle_data.get('BoundingBox') != ['0', '0', '0','0']:
            vehicle_crop_image = crop_image(image, vehicle_data.get('BoundingBox'))
            # vehicle_crop_image_webp = await convert_BytesIO_to_webp(vehicle_crop_image.getvalue())
            # vehicle_crop_image_webp_io = BytesIO(vehicle_crop_image_webp)
            name_image_vehicle = f'{name_file_iso}_VEHICLE.WEBP'
            url_vehicle = await minio_service.upload_file_from_bytesIO(vehicle_crop_image, name_image_vehicle)
        vehicle_result = {
            'Vehicle_BoundingBox': vehicle_data.get('BoundingBox', None),
            'Color_Vehicle': traffic_data.get('VehicleColor', None),
            'Vehicle_Type': vehicle_data.get('Category', None),
            'ID_Vehicle_Object': vehicle_data.get('ObjectID', None),
            'Name_Logo_Vehicle': vehicle_data.get('Text', None)
        }
        plate_result = {
            'Plate_BoundingBox': object_data.get('BoundingBox', None),
            'Color_Plate': traffic_data.get('PlateColor', None),
            'ID_Plate_Object': object_data.get('ObjectID', None),
            'Number_Plate': object_data.get('Text', None),
        }
        data_motor_save = {
            'Object_Detect':
                {
                    'NonMotor': None,
                    'Motor':
                        {
                            'Safe_Belt': {
                                'Main': data.get('CommInfo', {}).get('Seat', [None, None])[0],
                                'Slave': data.get('CommInfo', {}).get('Seat', [None, None])[1]
                            },
                            'Plate': plate_result,
                            'Vehicle': vehicle_result
                        }
                },
            'Image_Plate': url_plate,
            'Image_Vehicle': url_vehicle,
        }
        return data_motor_save
    async def handle_data_non_motor(self, minio_service, data, image, name_file_iso):
        url_vehicle = None
        name_image_plate, name_image_vehicle = self.get_name_image(name_file_iso)
        motorbike_data = data.get('NonMotor', {})
        rider_list = motorbike_data.get('RiderList', [])
        rider_data = rider_list[0] if rider_list else {}
        face_rider_data = rider_data.get('FaceAttributes', {})
        if motorbike_data.get('OriginalBoundingBox', None) is not None and motorbike_data.get('OriginalBoundingBox',None) != ['0', '0', '0','0']:
            vehicle_img_crop = crop_image_original(image, motorbike_data.get('OriginalBoundingBox', None))
            # vehicle_img_crop_webp = await convert_BytesIO_to_webp(vehicle_img_crop.getvalue())
            # vehicle_img_crop_webp_io = BytesIO(vehicle_img_crop_webp)
            url_vehicle = await minio_service.upload_file_from_bytesIO(vehicle_img_crop, name_image_vehicle)
        result_face_rider = {
            'Age': face_rider_data.get('Age', None),
            'Beard': self.to_enum(Beard_Human, face_rider_data.get('Beard', None)),
            'BoundingBox_Face_Rider': face_rider_data.get('BoundingBox', None),
            'Confidence_Face_Rider': face_rider_data.get('Confidence', None),
            'Emotion': face_rider_data.get('Emotion', None),
            'Eye': self.to_enum(Eye_Human, face_rider_data.get('Eye', None)),
            'Feature': face_rider_data.get('Feature', None),
            'Glass': self.to_enum(Glass_Human, face_rider_data.get('Glass', None)),
            'Hat': self.to_enum(Cap_Human, face_rider_data.get('Hat', None)),
            'Mask': self.to_enum(Mask_Human, face_rider_data.get('Mask', None)),
            'Mouth': self.to_enum(Mouth_Human, face_rider_data.get('Mouth', None)),
            'ObjectID_Of_Face': face_rider_data.get('ObjectID', None),
        }
        result_rider_data = {
            'Age': rider_data.get('Age', None),
            'Bag': self.to_enum(HasBag_Human, rider_data.get('Bag', None)),
            'Cap': self.to_enum(Cap_Human, rider_data.get('Cap', None)),
            'CarrierBag': self.to_enum(CarrierBag_Human, rider_data.get('CarrierBag', None)),
            'DownClothes': self.to_enum(DownClothes_Human, rider_data.get('DownClothes', None)),
            'HairStyle': self.to_enum(HairStyle_Human, rider_data.get('HairStyle', None)),
            'Helmet': self.to_enum(Helmet_Human, rider_data.get('Helmet', None)),
            'LowerBodyColor': rider_data.get('LowerBodyColor', None),
            'RainCoat': self.to_enum(RainCoat_Human, rider_data.get('RainCoat', None)),
            'Umbrella': self.to_enum(Umbrella_Human, rider_data.get('Umbrella', None)),
            'UpClothes': self.to_enum(UpClothes_Human, rider_data.get('UpClothes', None)),
            'UpperBodyColor': rider_data.get('UpperBodyColor', None),
            'Sex': rider_data.get('Sex', None),
            'Vehicle_BoundingBox': motorbike_data.get('OriginalBoundingBox', None)
        }
        data_nonmotor_save = {
            'Object_Detect': {
                'NonMotor':
                    {
                        'Vehicle_Type': motorbike_data.get('Category', None),
                        'Color_Vehicle': motorbike_data.get('Color', None),
                        'Number_Of_Cycling': motorbike_data.get('NumOfCycling', None),
                        'ObjectID_NonMotor': motorbike_data.get('ObjectID', None),
                        'Rider_Detect': result_rider_data,
                        'Face_Attributes': result_face_rider,
                    },
                'Motor': None
            },
            'Image_Plate': None,
            'Image_Vehicle': url_vehicle
        }
        return data_nonmotor_save
    async def save(self, data, image, device):
        minio_service = MinioServices()
        now = datetime.now().date()
        event_name = data.get('EventBaseInfo', {}).get('Code', 'Unknown')
        name_file_iso = f'{device.company.id}/{event_name}/{now}/{str(ObjectId())}'
        name_big_image = f'{name_file_iso}.WEBP'

        # Thông tin phân biệt loại xe(xe máy, ô tô)
        snap_category = data.get('CommInfo', {}).get('SnapCategory', 'Unknown')
        if snap_category == 'Motor':
            data_save = await self.handle_data_motor(minio_service, data, image, name_file_iso)
        elif snap_category == 'NonMotor':
            data_save = await self.handle_data_non_motor(minio_service, data, image, name_file_iso)
        else:
            return None

        image_webp = await convert_BytesIO_to_webp(image)
        convert_image_webp_io = BytesIO(image_webp)
        url = await minio_service.upload_file_from_bytesIO(convert_image_webp_io, name_big_image)
        data_shared = {
            'Channel': str(int(data.get('Channel', None))),
            'Event_ID': data.get('EventID', None),
            'Name_Event': data.get('EventBaseInfo', {}).get('Code', 'Unknown'),
            'Time': data.get('RealUTC', None),
            'Image': url,
        }
        data_save.update(data_shared)
        new_event = Event(
            event_type=EventTypeEnum.METADATA,
            data=data_save,
            company=device.company,
            device=device,
            camera=await self.get_ip_camera_by_channel_from_event(data.get('Channel', None))
        )
        await new_event.insert()
        print(f"Đã thêm {new_event} vào MongoDB.")
        return new_event