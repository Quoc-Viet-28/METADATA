import httpx
from fastapi import HTTPException

from app.constants.authorization_enum import AuthorizationEnum
from app.dto.authorization_dto import AuthorizationCreate
from app.models.webhook_model import WebHook
from app.services.webhook.WebHookFactory import WebHookFactory
from app.utils.call_api_httpx import post_data_auth


@WebHookFactory.register_class([AuthorizationEnum.BASIC_AUTH])
class AuthorizationBasic:
    def validate_create(self, webhook: AuthorizationCreate):
        if webhook.other_authorization.get('username') is None:
            raise HTTPException(status_code=400, detail="Vui lòng nhập username")
        if webhook.other_authorization.get('password') is None:
            raise HTTPException(status_code=400, detail="Vui lòng nhập password")
        return True

    async def send_request(self, webhook: WebHook, data):
        try:
            response = await post_data_auth(webhook.url,
                                            auth=httpx.BasicAuth(webhook.other_authorization.get('username'),
                                                                 webhook.other_authorization.get(
                                                                     'password')),
                                            data=data)
            return response
        except Exception as e:
            return None
