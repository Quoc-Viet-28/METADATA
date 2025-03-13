from fastapi import HTTPException, status, Query
from app.models.event_model import Event
from app.models.camera_model import Camera
import re
from app.utils.common_utils import get_company
class EventService:
    def __init__(self):
        pass
    async def get_data_by_event_ANPR(
            self,
            id_company,
            user,
            page=0,
            size=10,
            plate = None,
            color_vehicle = None,
            color_plate = None,
            vehicle_type = None,
            name_logo_vehicle = None,
    ):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "TRAFFIC"}, {"company": {"$ref": "Company", "$id": company.id}}]
        if plate:
            regex_plate = re.compile(f".*{plate}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Plate.Number_Plate": {"$regex": regex_plate}},
                    {"data.Object_Detect.NonMotor.Plate.Number_Plate": {"$regex": regex_plate}},
                ]
            })
        if color_vehicle:
            regex_color = re.compile(f".*{color_vehicle}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Vehicle.Color_Vehicle": {"$regex": regex_color}},
                    {"data.Object_Detect.NonMotor.Color_Vehicle": {"$regex": regex_color}},
                ]
            })
        if color_plate:
            regex_color_plate = re.compile(f".*{color_plate}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Plate.Color_Plate": {"$regex": regex_color_plate}},
                    {"data.Object_Detect.NonMotor.Plate.Color_Plate": {"$regex": regex_color_plate}},
                ]
            })
        if vehicle_type:
            regex_vehicle_type = re.compile(f".*{vehicle_type}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Vehicle.Vehicle_Type": {"$regex": regex_vehicle_type}},
                    {"data.Object_Detect.NonMotor.Vehicle_Type": {"$regex": regex_vehicle_type}},
                ]
            })
        if name_logo_vehicle:
            regex_name_logo_vehicle = re.compile(f".*{name_logo_vehicle}.*", re.IGNORECASE)
            query_conditions.append({
                    {"data.Object_Detect.Motor.Vehicle.Name_Logo_Vehicle": {"$regex": regex_name_logo_vehicle}},
             })
        query = {"$and": query_conditions} if query_conditions else {}
        plates = await Event.find(query).skip(page * size).limit(size).sort("-created_at").to_list()
        return plates
    async def get_count_by_event_ANPR(
            self,
            id_company,
            user,
            plate = None,
            color_vehicle = None,
            color_plate = None,
            vehicle_type = None,
            name_logo_vehicle = None,
    ):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "TRAFFIC"}, {"company": {"$ref": "Company", "$id": company.id}}]
        if plate:
            regex_plate = re.compile(f".*{plate}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Plate.Number_Plate": {"$regex": regex_plate}},
                    {"data.Object_Detect.NonMotor.Plate.Number_Plate": {"$regex": regex_plate}},
                ]
            })
        if color_vehicle:
            regex_color = re.compile(f".*{color_vehicle}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Vehicle.Color_Vehicle": {"$regex": regex_color}},
                    {"data.Object_Detect.NonMotor.Color_Vehicle": {"$regex": regex_color}},
                ]
            })
        if color_plate:
            regex_color_plate = re.compile(f".*{color_plate}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Plate.Color_Plate": {"$regex": regex_color_plate}},
                    {"data.Object_Detect.NonMotor.Plate.Color_Plate": {"$regex": regex_color_plate}},
                ]
            })
        if vehicle_type:
            regex_vehicle_type = re.compile(f".*{vehicle_type}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Vehicle.Vehicle_Type": {"$regex": regex_vehicle_type}},
                    {"data.Object_Detect.NonMotor.Vehicle_Type": {"$regex": regex_vehicle_type}},
                ]
            })
        if name_logo_vehicle:
            regex_name_logo_vehicle = re.compile(f".*{name_logo_vehicle}.*", re.IGNORECASE)
            query_conditions.append({
                    {"data.Object_Detect.Motor.Vehicle.Name_Logo_Vehicle": {"$regex": regex_name_logo_vehicle}},
             })
        query = {"$and": query_conditions} if query_conditions else {}
        plates = await Event.find(query).count()
        return plates

    async def get_data_by_event_METADATA(
            self,
            id_company,
            user,
            page= 0,
            size = 10,
            plate = None,
            color_vehicle = None,
            color_plate = None,
            vehicle_type = None,
            name_logo_vehicle = None,
            color_tshirt = None,
            color_pants = None,
            helmet = None,
            raincoat = None,
            mask = None,
    ):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "METADATA", "data.Name_Event": "TrafficJunction", "company": {"$ref": "Company", "$id": company.id}}]
        if plate:
            regex_plate = re.compile(f".*{plate}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Plate.Number_Plate": {"$regex": regex_plate}},
                    {"data.Object_Detect.NonMotor.Plate.Number_Plate": {"$regex": regex_plate}},
                ]
            })
        if color_vehicle:
            regex_color = re.compile(f".*{color_vehicle}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Vehicle.Color_Vehicle": {"$regex": regex_color}},
                    {"data.Object_Detect.NonMotor.Color_Vehicle": {"$regex": regex_color}},
                ]
            })
        if color_plate:
            regex_color_plate = re.compile(f".*{color_plate}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Plate.Color_Plate": {"$regex": regex_color_plate}},
                    {"data.Object_Detect.NonMotor.Plate.Color_Plate": {"$regex": regex_color_plate}},
                ]
            })
        if vehicle_type:
            regex_vehicle_type = re.compile(f".*{vehicle_type}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Vehicle.Vehicle_Type": {"$regex": regex_vehicle_type}},
                    {"data.Object_Detect.NonMotor.Vehicle_Type": {"$regex": regex_vehicle_type}},
                ]
            })
        if name_logo_vehicle:
            regex_name_logo_vehicle = re.compile(f".*{name_logo_vehicle}.*", re.IGNORECASE)
            query_conditions.append({
                    {"data.Object_Detect.Motor.Vehicle.Name_Logo_Vehicle": {"$regex": regex_name_logo_vehicle}}
            })
        if color_tshirt:
            regex_color_tshirt = re.compile(f".*{color_tshirt}.*", re.IGNORECASE)
            query_conditions.append(
                    {"data.Object_Detect.NonMotor.Rider_Detect.UpperBodyColor": {"$regex": regex_color_tshirt}}
            )
        if color_pants:
            regex_color_pants = re.compile(f".*{color_pants}.*", re.IGNORECASE)
            query_conditions.append(
                    {"data.Object_Detect.NonMotor.Rider_Detect.LowerBodyColor": {"$regex": regex_color_pants}}
            )
        if helmet:
            regex_helmet = re.compile(f".*{helmet}.*", re.IGNORECASE)
            query_conditions.append(
                    {"data.Object_Detect.NonMotor.Rider_Detect.Helmet": {"$regex": regex_helmet}}
            )
        if raincoat:
            regex_raincoat = re.compile(f".*{raincoat}.*", re.IGNORECASE)
            query_conditions.append(
                    {"data.Object_Detect.NonMotor.Rider_Detect.RainCoat": {"$regex": regex_raincoat}}
            )
        if mask:
            regex_mask = re.compile(f".*{mask}.*", re.IGNORECASE)
            query_conditions.append(
                    {"data.Object_Detect.NonMotor.Face_Attributes.Mask": {"$regex": regex_mask}}
            )
        query = {"$and": query_conditions} if query_conditions else {}
        data = await Event.find(query).skip(page * size).limit(size).sort("-created_at").to_list()
        return data
    async def get_count_by_event_METADATA(
            self,
            id_company,
            user,
            plate= None,
            color_vehicle= None,
            color_plate= None,
            vehicle_type= None,
            name_logo_vehicle= None,
            color_tshirt= None,
            color_pants= None,
            helmet = None,
            raincoat = None,
            mask = None):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "METADATA", "data.Name_Event": "TrafficJunction",
                             "company": {"$ref": "Company", "$id": company.id}}]
        if plate:
            regex_plate = re.compile(f".*{plate}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Plate.Number_Plate": {"$regex": regex_plate}},
                    {"data.Object_Detect.NonMotor.Plate.Number_Plate": {"$regex": regex_plate}},
                ]
            })
        if color_vehicle:
            regex_color = re.compile(f".*{color_vehicle}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Vehicle.Color_Vehicle": {"$regex": regex_color}},
                    {"data.Object_Detect.NonMotor.Color_Vehicle": {"$regex": regex_color}},
                ]
            })
        if color_plate:
            regex_color_plate = re.compile(f".*{color_plate}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Plate.Color_Plate": {"$regex": regex_color_plate}},
                    {"data.Object_Detect.NonMotor.Plate.Color_Plate": {"$regex": regex_color_plate}},
                ]
            })
        if vehicle_type:
            regex_vehicle_type = re.compile(f".*{vehicle_type}.*", re.IGNORECASE)
            query_conditions.append({
                "$or": [
                    {"data.Object_Detect.Motor.Vehicle.Vehicle_Type": {"$regex": regex_vehicle_type}},
                    {"data.Object_Detect.NonMotor.Vehicle_Type": {"$regex": regex_vehicle_type}},
                ]
            })
        if name_logo_vehicle:
            regex_name_logo_vehicle = re.compile(f".*{name_logo_vehicle}.*", re.IGNORECASE)
            query_conditions.append({
                {"data.Object_Detect.Motor.Vehicle.Name_Logo_Vehicle": {"$regex": regex_name_logo_vehicle}}
            })
        if color_tshirt:
            regex_color_tshirt = re.compile(f".*{color_tshirt}.*", re.IGNORECASE)
            query_conditions.append(
                {"data.Object_Detect.NonMotor.Rider_Detect.UpperBodyColor": {"$regex": regex_color_tshirt}}
            )
        if color_pants:
            regex_color_pants = re.compile(f".*{color_pants}.*", re.IGNORECASE)
            query_conditions.append(
                {"data.Object_Detect.NonMotor.Rider_Detect.LowerBodyColor": {"$regex": regex_color_pants}}
            )
        if helmet:
            regex_helmet = re.compile(f".*{helmet}.*", re.IGNORECASE)
            query_conditions.append(
                {"data.Object_Detect.NonMotor.Rider_Detect.Helmet": {"$regex": regex_helmet}}
            )
        if raincoat:
            regex_raincoat = re.compile(f".*{raincoat}.*", re.IGNORECASE)
            query_conditions.append(
                {"data.Object_Detect.NonMotor.Rider_Detect.RainCoat": {"$regex": regex_raincoat}}
            )
        if mask:
            regex_mask = re.compile(f".*{mask}.*", re.IGNORECASE)
            query_conditions.append(
                {"data.Object_Detect.NonMotor.Face_Attributes.Mask": {"$regex": regex_mask}}
            )
        query = {"$and": query_conditions} if query_conditions else {}
        count = await Event.find(query).count()
        return count


    async def get_data_by_event_FACE(self, id_company, user, page = 0, size = 10, id_card_person = None, name_person = None):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "FACE"}, {"company": {"$ref": "Company", "$id": company.id}}]
        if id_card_person:
            regex_id_card = re.compile(f".*{id_card_person}.*", re.IGNORECASE)
            query_conditions.append({"data.Candidates.ID_Card": {"$regex": regex_id_card}})
        if name_person:
            regex_name = re.compile(f".*{name_person}.*", re.IGNORECASE)
            query_conditions.append({"data.Candidates.Name": {"$regex": regex_name}})
        query = {"$and": query_conditions} if query_conditions else {}
        faces = await Event.find(query).skip(page * size).limit(size).sort("-created_at").to_list()
        return faces
    async def get_count_by_event_FACE(self, id_company, user, id_card_person = None, name_person = None):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "FACE"}, {"company": {"$ref": "Company", "$id": company.id}}]
        if id_card_person:
            regex_id_card = re.compile(f".*{id_card_person}.*", re.IGNORECASE)
            query_conditions.append({"data.Candidates.ID_Card": {"$regex": regex_id_card}})
        if name_person:
            regex_name = re.compile(f".*{name_person}.*", re.IGNORECASE)
            query_conditions.append({"data.Candidates.Name": {"$regex": regex_name}})
        query = {"$and": query_conditions} if query_conditions else {}
        count = await Event.find(query).count()
        return count
    async def get_image_by_ip_camera_from_crossline(self, id_company, id_device ,ip_camera, user, page = 0, size = 10, time_left_to_right = None, time_right_to_left = None, total_time = None):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "CROSSLINE"}, {"company": {"$ref": "Company", "$id": company.id}}, {"device": {"$ref": "Device", "$id": id_device}}]
        if ip_camera:
            regex_ip_camera = re.compile(f".*{ip_camera}.*", re.IGNORECASE)
            camera = await Camera.find_one({"ip_camera": {"$regex": regex_ip_camera}})
            if not camera:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy camera"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST)
        if camera.id:
            query_conditions.append({"camera": {"$ref": "Camera", "$id": camera.id}})
        else:
            return {"error": "No camera found with the provided IP"}
        if time_left_to_right:
            regex_time_left_to_right = re.compile(f".*{time_left_to_right}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Time_LeftToRight": {"$regex": regex_time_left_to_right}})
        if time_right_to_left:
            regex_time_right_to_left = re.compile(f".*{time_right_to_left}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Time_RightToLeft": {"$regex": regex_time_right_to_left}})
        if total_time:
            regex_total_time = re.compile(f".*{total_time}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Total_time": {"$regex": regex_total_time}})
        query = {"$and": query_conditions} if query_conditions else {}
        images = await Event.find(query).skip(page * size).limit(size).sort("-created_at").to_list()
        return images
    async def get_count_image_by_ip_camera_from_crossline(self, id_company, id_device, ip_camera, user, time_left_to_right = None, time_right_to_left = None, total_time = None):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "CROSSLINE"}, {"company": {"$ref": "Company", "$id": company.id}}, {"device": {"$ref": "Device", "$id": id_device}}]
        if ip_camera:
            regex_ip_camera = re.compile(f".*{ip_camera}.*", re.IGNORECASE)
            camera = await Camera.find_one({"ip_camera": {"$regex": regex_ip_camera}})
            if not camera:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy camera"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST)
        if camera.id:
            query_conditions.append({"camera": {"$ref": "Camera", "$id":camera.id}})
        else:
            return {"error": "No camera found with the provided IP"}
        if time_left_to_right:
            regex_time_left_to_right = re.compile(f".*{time_left_to_right}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Time_LeftToRight": {"$regex": regex_time_left_to_right}})
        if time_right_to_left:
            regex_time_right_to_left = re.compile(f".*{time_right_to_left}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Time_RightToLeft": {"$regex": regex_time_right_to_left}})
        if total_time:
            regex_total_time = re.compile(f".*{total_time}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Total_Time": {"$regex": regex_total_time}})
        query = {"$and": query_conditions} if query_conditions else {}
        count = await Event.find(query).count()
        return count

    async def get_image_by_ip_camera_from_crossregion(self, id_company, id_device, ip_camera, user, page = 0, size = 10, time_enter=None, time_leave=None, total_time=None):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "CROSSREGION"}, {"company": {"$ref": "Company", "$id": company.id}},
                            {"device": {"$ref": "Device", "$id": id_device}}]
        if ip_camera:
            regex_ip_camera = re.compile(f".*{ip_camera}.*", re.IGNORECASE)
            camera = await Camera.find_one({"ip_camera": {"$regex": regex_ip_camera}})
            if not camera:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy camera"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST)
        if camera.id:
            query_conditions.append({"camera": {"$ref": "Camera", "$id": camera.id}})
        else:
            return {"error": "No camera found with the provided IP"}
        if time_enter:
            regex_time_enter = re.compile(f".*{time_enter}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Time_Enter": {"$regex": regex_time_enter}})
        if time_leave:
            regex_time_leave = re.compile(f".*{time_leave}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Time_Leave": {"$regex": regex_time_leave}})
        if total_time:
            regex_total_time = re.compile(f".*{total_time}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Total_Time": {"$regex": regex_total_time}})
        query = {"$and": query_conditions} if query_conditions else {}
        images = await Event.find(query).skip(page * size).limit(size).sort("-created_at").to_list()
        return images
    async def get_count_image_by_ip_camera_from_crossregion(self, id_company, id_device, ip_camera, user, time_enter=None, time_leave=None, total_time=None):
        company = await get_company(user, id_company)
        query_conditions = [{"event_type": "CROSSREGION"}, {"company": {"$ref": "Company", "$id": company.id}},
                            {"device": {"$ref": "Device", "$id": id_device}}]
        if ip_camera:
            regex_ip_camera = re.compile(f".*{ip_camera}.*", re.IGNORECASE)
            camera = await Camera.find_one({"ip_camera": {"$regex": regex_ip_camera}})
            if not camera:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy camera"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST)
        if camera.id:
            query_conditions.append({"camera": {"$ref": "Camera", "$id": camera.id}})
        else:
            return {"error": "No camera found with the provided IP"}
        if time_enter:
            regex_time_enter = re.compile(f".*{time_enter}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Time_Enter": {"$regex": regex_time_enter}})
        if time_leave:
            regex_time_leave = re.compile(f".*{time_leave}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Time_Leave": {"$regex": regex_time_leave}})
        if total_time:
            regex_total_time = re.compile(f".*{total_time}.*", re.IGNORECASE)
            query_conditions.append({"data.Time.Total_Time": {"$regex": regex_total_time}})
        query = {"$and": query_conditions} if query_conditions else {}
        count = await Event.find(query).count()
        return count

event_service= EventService()