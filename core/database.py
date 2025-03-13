import pandas as pd
import unidecode
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Link
from app.core.setting_env import settings
import os
import importlib
from typing import List, Type
from beanie import Document

from app.models.district_model import District
from app.models.province_model import Province
from app.models.ward_model import Ward
from pathlib import Path


# Company
csv_ward_path = Path(__file__).parent / 'data' / 'wards.csv'
csv_district_path = Path(__file__).parent / 'data' /'districts.csv'
csv_province_path = Path(__file__).parent / 'data' /'provinces.csv'

# Function to automatically load all Document models from the models directory
def load_document_models() -> List[Type[Document]]:
    # Xác định thư mục chứa models từ thư mục hiện tại
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Lấy thư mục cha của "core"
    models_dir = os.path.join(base_dir, "models")  # Tạo đường dẫn tới thư mục models
    document_models = []
    # Duyệt qua các file trong thư mục models
    for filename in os.listdir(models_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"app.models.{filename[:-3]}"
            module = importlib.import_module(module_name)
            # Lấy tất cả các lớp kế thừa từ Document trong module
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type) and issubclass(attribute, Document):
                    document_models.append(attribute)
    return document_models
async def insert_provinces_from_csv(csv_file_path):
    data = pd.read_csv(csv_file_path)
    for _, row in data.iterrows():
        _id = row['id']
        if 'provinces.csv' in csv_file_path:
            existing_province = await Province.find_one({"_id": _id})
            if existing_province:
                pass
            else:
                new_province = Province(
                    id=_id,
                    name_search=unidecode.unidecode(row['name']).lower(),
                    code=row['code'],
                    name=row['name']
                )
                await new_province.insert()
                print(f"Đã thêm {new_province} vào MongoDB.")
        elif 'districts.csv' in csv_file_path:
            existing_district = await District.find_one({"_id": _id})
            if existing_district:
                pass
            else:
                province= await Province.find_one({"_id": row['province_id']})
                new_district = District(
                    id=_id,
                    code=row['code'],
                    name=row['name'],
                    name_search=unidecode.unidecode(row['name']).lower(),
                    province= province
                )
                await new_district.insert()
                print(f"Đã thêm {new_district} vào MongoDB.")
        elif 'wards.csv' in csv_file_path:
            existing_ward = await Ward.find_one({"_id": _id})
            if existing_ward:
                pass
            else:
                district = await District.find_one({"_id": row['district_id']})
                new_ward = Ward(
                    id=_id,
                    code=row['code'],
                    name=row['name'],
                    name_search=unidecode.unidecode(row['name']).lower(),
                    district=district
                )
                await new_ward.insert()
                print(f"Đã thêm {new_ward} vào MongoDB.")
async def init_db():
    # Load all Document models from the models directory
    document_models = load_document_models()
    # Create Motor client
    client = AsyncIOMotorClient(settings.MONGO_DATABASE_URI)
    client_db = client[settings.MONGO_DATABASE]  # Connect to the database
    # Initialize Beanie with the loaded document models
    await init_beanie(database=client_db, document_models=document_models)
    if await Province.count() == 0:
        await insert_provinces_from_csv(str(csv_province_path))
    if await District.count() == 0:
        await insert_provinces_from_csv(str(csv_district_path))
    if await Ward.count() == 0:
        await insert_provinces_from_csv(str(csv_ward_path))



