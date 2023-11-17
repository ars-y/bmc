from enum import Enum


class TokenEnum(str, Enum):

    ACCESS = 'access_token'
    REFRESH = 'refresh_token'
    RESET = 'reset_token'
