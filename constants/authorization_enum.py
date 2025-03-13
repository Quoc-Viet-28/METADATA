from enum import Enum


class AuthorizationEnum(Enum):
    NO_AUTH = "NO_AUTH"
    BASIC_AUTH = "BASIC_AUTH"
    Bearer_TOKEN = "Bearer_TOKEN"
    # JWt_BEARER = "JWt_BEARER"
    DIGEST_AUTH = "DIGEST_AUTH"
