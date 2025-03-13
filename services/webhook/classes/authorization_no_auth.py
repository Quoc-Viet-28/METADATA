
from app.constants.authorization_enum import AuthorizationEnum
from app.dto.authorization_dto import AuthorizationCreate
from app.models.webhook_model import WebHook
from app.services.webhook.WebHookFactory import WebHookFactory
from app.utils.call_api_httpx import post_data_auth


@WebHookFactory.register_class([AuthorizationEnum.NO_AUTH])
class AuthorizationNoAuth:
    def validate_create(self, webhook: AuthorizationCreate):
        return True

    async def send_request(self, webhook: WebHook, data):
        try:
            response = await post_data_auth(webhook.url,
                                            auth=None,
                                            data=data)
            return response
        except Exception as e:
            return None
