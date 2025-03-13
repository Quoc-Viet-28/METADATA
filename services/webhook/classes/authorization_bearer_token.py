from fastapi import HTTPException

from app.constants.authorization_enum import AuthorizationEnum
from app.dto.authorization_dto import AuthorizationCreate
from app.models.webhook_model import WebHook
from app.services.webhook.WebHookFactory import WebHookFactory
from app.utils.call_api_httpx import post_data_auth


@WebHookFactory.register_class([AuthorizationEnum.Bearer_TOKEN])
class AuthorizationBearerToken:
    def validate_create(self, webhook: AuthorizationCreate):
        if webhook.other_authorization.get('token') is None:
            raise HTTPException(status_code=400, detail="Vui lòng nhập token")
        return True

    async def send_request(self, webhook: WebHook, data):
        try:
            response = await post_data_auth(webhook.url,
                                            auth=None,
                                            data=data, headers={
                    'Authorization': 'Bearer ' + webhook.other_authorization.get('token')})
            return response
        except Exception as e:
            return None
