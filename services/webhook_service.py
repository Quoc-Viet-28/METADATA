import unidecode
from beanie import PydanticObjectId
from fastapi import HTTPException

from app.dto.authorization_dto import AuthorizationCreate, AuthorizationUpdate
from app.models.webhook_model import WebHook
from app.services.webhook.WebHookFactory import WebHookFactory
from app.utils.common_utils import get_company


class WebHookService:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebHookService, cls).__new__(cls)
        return cls.instance

    async def create(self, webhook: AuthorizationCreate, user):
        deviceFactory = WebHookFactory.add_class(webhook.authorization)
        deviceFactory.validate_create(webhook)
        company = await get_company(user, webhook.id_company)
        new_data = WebHook(
            **webhook.dict(exclude={"id_company", }),  # Loại bỏ id_company
            company=company,  # Gán công ty cho thiết bị
            name_search=unidecode.unidecode(webhook.name).lower(),
            is_active=True

        )
        await new_data.insert()
        return new_data

    async def update(self, webhook: AuthorizationUpdate, user):

        authorization = await WebHook.get(webhook.id)
        if authorization is None:
            raise HTTPException(status_code=400, detail="Không tìm thấy webhook")

        update_data = webhook.dict(exclude_unset=True, exclude={"id_company"})
        for field, value in update_data.items():
            setattr(authorization, field, value)

        if webhook.id_company is not None:
            company = await get_company(user, webhook.id_company)
            authorization.company = company

        authorization.name_search = unidecode.unidecode(authorization.name).lower()

        deviceFactory = WebHookFactory.add_class(authorization.authorization)
        deviceFactory.validate_create(authorization)
        await authorization.replace()
        return authorization

    async def delete(self, id):
        authorization = await WebHook.get(id)
        if authorization is None:
            raise HTTPException(status_code=400, detail="Không tìm thấy webhook")
        await authorization.delete()
        return True

    async def get_all(self, page, size, key_work, id_company: PydanticObjectId, user):
        # Lấy thông tin công ty
        company = await get_company(user, id_company)

        # Xây dựng bộ lọc
        filter_criteria = {
            "company": {
                "$ref": "Company",
                "$id": company.id
            }
        }

        # Thêm điều kiện tìm kiếm nếu key_work có giá trị
        if key_work is not None:
            filter_criteria["name_search"] = {
                "$regex": unidecode.unidecode(key_work).lower()
            }

        # Thực hiện truy vấn
        return await WebHook.find(filter_criteria, skip=page * size, limit=size).sort("-created_at").to_list()

    async def get_count(self, key_work, id_company: PydanticObjectId, user):
        # Lấy thông tin công ty
        company = await get_company(user, id_company)

        # Xây dựng bộ lọc
        filter_criteria = {
            "company": {
                "$ref": "Company",
                "$id": company.id
            }
        }

        # Thêm điều kiện tìm kiếm nếu key_work có giá trị
        if key_work is not None:
            filter_criteria["name_search"] = {
                "$regex": key_work
            }

        # Thực hiện truy vấn
        return await WebHook.find(filter_criteria).count()
