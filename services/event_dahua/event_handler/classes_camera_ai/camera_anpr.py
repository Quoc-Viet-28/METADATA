import json
import asyncio
import time
from datetime import datetime
from io import BytesIO

from bson import ObjectId

from app.constants.event_data_enum import Cap_Human, DownClothes_Human, HairStyle_Human, HasHat_Human, \
    Helmet_Human, RainCoat_Human, Umbrella_Human, UpClothes_Human, HasBag_Human, MessengerBag_Human, ShoulderBag_Human, \
    CarrierBag_Human
from app.constants.event_type_emum import EventTypeEnum
from app.models.event_model import Event
from app.services.event_dahua.event_handler.event_handler_camera_ai_factory import EventHandlerCameraAIFactory
from app.services.event_dahua.image_helper import crop_image, crop_image_original
from app.utils.image_processing import convert_BytesIO_to_webp
from app.utils.minio_utils import MinioServices


@EventHandlerCameraAIFactory.register_class(
    ['TrafficJunction', 'TrafficRetrograde', 'TrafficOverline', 'TrafficOverSpeed'
        , 'TrafficNonMotorInMotorRoute', 'TrafficNonMotorWithoutSafehat'
        , 'TrafficWithoutSafeBelt', 'TrafficAssistantWithoutSafeBelt'
        , 'TrafficDriverSmoking', 'TrafficDriverCalling', 'TrafficCrossLane'])
class TrafficANPRHandler:

    def __init__(self, type_name):
        self.type_name = type_name

    def to_enum(self, enum_class, value):
        try:
            return str(enum_class(value).name)
        except ValueError:
            return None

    def get_name_image(self, name_file_iso):
        name_image_plate = f'{name_file_iso}_PLATE.WEBP'
        name_image_vehicle = f'{name_file_iso}_VEHICLE.WEBP'
        name_image_face = f'{name_file_iso}_FACE.WEBP'
        name_image_car_window = f'{name_file_iso}_CAR_WINDOW.WEBP'
        return name_image_plate, name_image_vehicle, name_image_face, name_image_car_window

    async def handle_moto(self, minio_service, data, image, name_file_iso):
        name_image_plate, name_image_vehicle, name_image_face, name_image_car_window = self.get_name_image(
            name_file_iso)
        url_plate = None
        url_vehicle = None
        url_car_window = None
        url_face_driver = None
        url_face_passenger = None
        driver_face = data.get('CommInfo', {}).get('Drivers', [])

        plate_bounding_box = data.get('Object', {}).get('OriginalBoundingBox', None)
        vehicle_bounding_box = data.get('Vehicle', {}).get('OriginalBoundingBox', None)
        car_window_bounding_box = data.get('Vehicle', {}).get('CarWindow', None).get('BoundingBox', None)
        if data.get('Object', {}).get('Text', None) is not None and data.get('Object', {}).get('Text', None) != "":
            if plate_bounding_box is not None and plate_bounding_box != ["0", "0", "0", "0"] and all(
                    value is not None for value in plate_bounding_box):
                plate_crop_image = crop_image_original(image, plate_bounding_box)
                # plate_crop_image_webp = await convert_BytesIO_to_webp(plate_crop_image.getvalue())
                # plate_crop_image_webp_io = BytesIO(plate_crop_image_webp)
                url_plate = await minio_service.upload_file_from_bytesIO(plate_crop_image, name_image_plate)

        if vehicle_bounding_box is not None and vehicle_bounding_box != ["0", "0", "0", "0"] and all(
                value is not None for value in vehicle_bounding_box):
            vehicle_crop_image = crop_image_original(image, vehicle_bounding_box)
            # vehicle_crop_image_webp = await convert_BytesIO_to_webp(vehicle_crop_image.getvalue())
            # vehicle_crop_image_webp_io = BytesIO(vehicle_crop_image_webp)
            url_vehicle = await minio_service.upload_file_from_bytesIO(vehicle_crop_image, name_image_vehicle)

        if car_window_bounding_box is not None and car_window_bounding_box != ['0', '0', '0', '0'] and all(
                value is not None for value in car_window_bounding_box):
            car_window_crop_image = crop_image(image,
                                               data.get('Vehicle', {}).get('CarWindow', None).get('BoundingBox', None))
            # car_window_crop_image_webp = await convert_BytesIO_to_webp(car_window_crop_image.getvalue())
            # car_window_crop_image_webp_io = BytesIO(car_window_crop_image_webp)
            url_car_window = await minio_service.upload_file_from_bytesIO(car_window_crop_image,
                                                                          name_image_car_window)
        if len(driver_face) > 0:
            for i, driver in enumerate(driver_face):
                original_bbox = driver.get('OriginalBoundingBox', None)
                if original_bbox is not None and original_bbox != ["0", "0", "0", "0"] and all(
                        value is not None for value in original_bbox):

                    bbox = [int(coord) for coord in original_bbox]

                    if driver.get('ObjectType', None) == 'DriverFace':
                        cropped_image = crop_image_original(actual_content=image, bbox=bbox)
                        # cropped_image_webp = await convert_BytesIO_to_webp(cropped_image.getvalue())
                        # cropped_image_webp_io = BytesIO(cropped_image_webp)
                        url_face_driver = await minio_service.upload_file_from_bytesIO(cropped_image,
                                                                                       f'{name_file_iso}_face_motor_driver.WEBP')
                    elif driver.get('ObjectType', None) == 'AssistantDriverFace':
                        cropped_image = crop_image_original(actual_content=image, bbox=bbox)
                        # cropped_image_webp = await convert_BytesIO_to_webp(cropped_image.getvalue())
                        # cropped_image_webp_io = BytesIO(cropped_image_webp)
                        url_face_passenger = await minio_service.upload_file_from_bytesIO(cropped_image,
                                                                                          f'{name_file_iso}_face_motor_passenger.WEBP')

        data_motor_save = {
            'Object_Detect': {
                'NonMotor': None,
                'Motor': {
                    'Safe_Belt': {
                        'Main': data.get('CommInfo', {}).get('Seat', [None, None])[0],
                        'Slave': data.get('CommInfo', {}).get('Seat', [None, None])[1]
                    },
                    'Plate': {
                        'ID_Plate': data.get('Object', {}).get('BelongID', None),
                        'Bounding_Box_Plate': data.get('Object', {}).get('OriginalBoundingBox', None),
                        'Confidence': data.get('Object', {}).get('Confidence', None),
                        'Number_Plate': data.get('Object', {}).get('Text', None),
                        'Color_Plate': data.get('TrafficCar', {}).get('PlateColor', None),
                    },
                    'Vehicle': {
                        'Vehicle_BoundingBox': data.get('Vehicle', {}).get('OriginalBoundingBox', None),
                        'Color_Vehicle': data.get('TrafficCar', {}).get('VehicleColor', None),
                        'Vehicle_Type': data.get('CommInfo', {}).get('StandardVehicleType', None),
                        'Size_Vehicle': data.get('TrafficCar', {}).get('VehicleSize', None),
                        'Name_Logo_Vehicle': data.get('TrafficCar', {}).get('VehicleSign', None),
                        'Flow_Direction': data.get('TrafficCar', {}).get('CustomFlowDirection', None),
                        'Lower_Speed_Limit': data.get('TrafficCar', {}).get('LowerSpeedLimit', None),
                        'Upper_Speed_Limit': data.get('TrafficCar', {}).get('UpperSpeedLimit', None),
                        'UnderSpeedMargin': data.get('TrafficCar', {}).get('UnderSpeedMargin', None),
                        'OverSpeedMargin': data.get('TrafficCar', {}).get('OverSpeedMargin', None),
                        'Speed': data.get('TrafficCar', {}).get('Speed', None),
                        'Car_Window_Bounding_Box': data.get('Vehicle', {}).get('CarWindow', None).get('BoundingBox',
                                                                                                      None),
                    }
                }
            },
            'Image_Plate': url_plate,
            'Image_Vehicle': url_vehicle,
            'Image_Car_Window': url_car_window,
            'Image_Face_NonMotor': None,
            'Image_Driver_Face': url_face_driver,
            'Image_Passenger_Face': url_face_passenger
        }

        return data_motor_save

    async def handle_non_moto(self, minio_service, data, image, name_file_iso):
        name_image_plate, name_image_vehicle, name_image_face, name_image_car_window = self.get_name_image(
            name_file_iso)
        motorbike_data = data.get('NonMotor', {})
        rider_list = motorbike_data.get('RiderList', [])
        rider_data = rider_list[0] if rider_list else {}
        plate_bounding_box = data.get('NonMotor', {}).get('Plate', {}).get('OriginalBoundingBox', None)
        vehicle_bounding_box = data.get('Vehicle', {}).get('OriginalBoundingBox', None)
        url_plate = None
        url_vehicle = None
        url_face = None
        if data.get('NonMotor', {}).get('Plate', {}).get('Text', None) is not None and data.get('NonMotor', {}).get('Plate', {}).get('Text', None) != "":
            if plate_bounding_box is not None and plate_bounding_box != ["0", "0", "0", "0"] and all(
                    value is not None for value in plate_bounding_box):
                plate_crop_image = crop_image_original(image, plate_bounding_box)
                url_plate = await minio_service.upload_file_from_bytesIO(plate_crop_image, name_image_plate)
        if vehicle_bounding_box is not None and vehicle_bounding_box != ["0", "0", "0", "0"] and all(
                value is not None for value in vehicle_bounding_box):
            vehicle_crop_image = crop_image_original(image, vehicle_bounding_box)
            url_vehicle = await minio_service.upload_file_from_bytesIO(vehicle_crop_image, name_image_vehicle)

        if data.get('Vehicle', {}).get('OriginalBoundingBox', None) is not None and data.get('Vehicle', {}).get('OriginalBoundingBox', None) != ["0", "0", "0", "0"]:
            # width_face=int(rider_data.get("FaceImage", {}).get("Width"))
            height_face = int(rider_data.get("FaceImage", {}).get("Height", 0))
            coors_face_pre = data.get('Vehicle', {}).get('OriginalBoundingBox', None)
            top_left_x = int(coors_face_pre[0])
            top_left_y = int(coors_face_pre[1])
            bottom_right_x = int(coors_face_pre[2])
            coors_face = [top_left_x, top_left_y, bottom_right_x, top_left_y + height_face]
            face_crop_image = crop_image_original(image, coors_face)
            url_face = await minio_service.upload_file_from_bytesIO(face_crop_image, name_image_face)
        data_nonmotor_save = {
            'Object_Detect': {
                'NonMotor': {
                    'Vehicle_Type': data.get('NonMotor', {}).get('Category', None),
                    'Color_Vehicle': data.get('NonMotor', {}).get('Color', None),
                    'Num_Of_Cycling': data.get('NonMotor', {}).get('NumOfCycling', None),
                    'NonMotor_Bounding_Box': data.get('Vehicle', {}).get('OriginalBoundingBox', None),
                    'Speed': data.get('TrafficCar', {}).get('Speed', None),
                    'Plate': {
                        'Plate_Bounding_Box': data.get('NonMotor', {}).get('Plate', {}).get('OriginalBoundingBox',
                                                                                            None),
                        'Number_Plate': data.get('NonMotor', {}).get('Plate', {}).get('Text', None),
                        'Color_Plate': data.get('TrafficCar', {}).get('PlateColor', None),
                    },
                    'RiderList': {
                        'Bag': self.to_enum(HasBag_Human, rider_data.get('Bag', None)),
                        'MessengerBag': self.to_enum(MessengerBag_Human, rider_data.get('MessengerBag', None)),
                        'ShoulderBag': self.to_enum(ShoulderBag_Human, rider_data.get('ShoulderBag', None)),
                        'CarrierBag': self.to_enum(CarrierBag_Human, rider_data.get('CarrierBag', None)),
                        'Cap': self.to_enum(Cap_Human, rider_data.get('Cap', None)),
                        'DownClothes': self.to_enum(DownClothes_Human, rider_data.get('DownClothes', None)),
                        'HairStyle': self.to_enum(HairStyle_Human, rider_data.get('HairStyle', None)),
                        'HasHat': self.to_enum(HasHat_Human, rider_data.get('HasHat', None)),
                        'Helmet': self.to_enum(Helmet_Human, rider_data.get('Helmet', None)),
                        'LowerBodyColor': rider_data.get('LowerBodyColor', None),
                        'RainCoat': self.to_enum(RainCoat_Human, rider_data.get('RainCoat', None)),
                        'Umbrella': self.to_enum(Umbrella_Human, rider_data.get('Umbrella', None)),
                        'UpClothes': self.to_enum(UpClothes_Human, rider_data.get('UpClothes', None)),
                        'UpperBodyColor': rider_data.get('UpperBodyColor', None),
                        'Bounding_Box_Face': rider_data.get('FaceAttributes', {}).get('OriginalBoundingBox'),
                    }
                },
                'Motor': None
            },
            'Image_Plate': url_plate,
            'Image_Vehicle': url_vehicle,
            'Image_Car_Window': None,
            'Image_Face_NonMotor': url_face,
            'Image_Driver_Face': None,
            'Image_Passenger_Face': None,
        }
        return data_nonmotor_save

    async def save(self, data, image, device):
        minio_service = MinioServices()

        now = datetime.now().date()
        event_name = data.get('EventBaseInfo', {}).get('Code', 'Unknown')
        if event_name == 'TrafficNonMotorInMotorRoute':
            with open(f'TEST_TrafficNonMotorInMotorRoute.json', 'w') as f:
                json.dump(data, f, indent=4)
        name_file_iso = f'{device.company.id}/{event_name}/{now}/{str(ObjectId())}'
        name_big_image = f'{name_file_iso}.WEBP'

        # thong tin loại xe là Motor( xe 4 bánh) NONMotor( xe 2 bánh)
        snap_category = data.get('CommInfo', {}).get('SnapCategory', 'Unknown')
        if snap_category == 'Motor':
            data_save = await self.handle_moto(minio_service, data, image, name_file_iso)
        elif snap_category == 'NonMotor':
            data_save = await self.handle_non_moto(minio_service, data, image, name_file_iso)
        else:
            return None
        image_webp = await convert_BytesIO_to_webp(image)
        convert_image_webp_io = BytesIO(image_webp)
        url = await minio_service.upload_file_from_bytesIO(convert_image_webp_io, name_big_image)
        data_share = {
            'Event_ID': data.get('EventID', None),
            'Machine_ID': data.get('TrafficCar', {}).get('MachineName', None),
            'Name_Event': data.get('EventBaseInfo', {}).get('Code', None),
            'Lane': data.get('Lane', None),
            'Junction_Direction': data.get('JunctionDirection', None),
            'Name_Of_Road': data.get('Name', None),
            'Violation_Name': data.get('TrafficCar', {}).get('ViolationName', None),
            'Time': data.get('UTC', None),
            'Image': url,

        }

        data_save.update(data_share)

        new_event = Event(
            event_type=EventTypeEnum.TRAFFIC,
            data=data_save,
            company=device.company,
            device=device
        )
        await new_event.insert()
        print(f"Đã thêm {new_event} vào MongoDB.")
        return new_event
