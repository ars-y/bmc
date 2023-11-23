from datetime import datetime, timedelta

import jwt

from src.core.settings.auth import auth_settings
from src.exceptions.auth import InvalidToken
from src.exceptions.common import NotSupportedMethodError
from src.utils.jwt import decode, generate
from src.enums.token import TokenEnum
from src.models.user import User
from src.services.bases import TokenAbstractBaseService


class JWTService(TokenAbstractBaseService):

    _key: str
    _algorithm: str
    _exp_minutes: dict[TokenEnum, int]

    def __init__(self) -> None:
        self._key = auth_settings.JWT_SECRET
        self._algorithm = auth_settings.JWT_ALGORITHM
        self._exp_minutes = {
            TokenEnum.ACCESS: auth_settings.ACCESS_JWT_EXPIRE_MINUTES,
            TokenEnum.REFRESH: auth_settings.REFRESH_JWT_EXPIRE_MINUTES,
            TokenEnum.RESET: auth_settings.RESET_JWT_EXPIRE_MINUTES
        }

    async def write(self, user: User) -> dict:
        data: dict = {'sub': str(user.id)}
        access_token = await self._generate_jwt(data, TokenEnum.ACCESS)
        refresh_token = await self._generate_jwt(data, TokenEnum.REFRESH)

        return {
            'access': access_token,
            'refresh': refresh_token
        }

    async def read(self, token: str) -> dict:
        try:
            return decode(token, self._key, [self._algorithm])

        except jwt.ExpiredSignatureError:
            raise InvalidToken()
        except jwt.PyJWTError:
            raise InvalidToken()

    async def remove(self, token: str) -> None:
        raise NotSupportedMethodError(
            'JSON Web Token is valid until it expires'
        )

    async def _generate_jwt(self, data: dict, token_type: TokenEnum) -> str:
        exp_minutes: int = self._exp_minutes[token_type]
        expire = datetime.utcnow() + timedelta(minutes=exp_minutes)
        data.update({
            'exp': expire,
            'type': token_type
        })
        return generate(data, self._key, self._algorithm)


jwt_service = JWTService()
