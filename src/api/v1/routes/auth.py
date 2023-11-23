from typing import Optional

from fastapi import APIRouter, status

from src.api.v1.schemas.request.auth import AuthUser
from src.api.v1.schemas.request.user import UserCreateSchema
from src.api.v1.schemas.response.user import UserResponseSchema
from src.cache.redis import RedisClient
from src.dependencies import UOWDep
from src.models import User
from src.services import (
    UserService,
    jwt_service
)
from src.services.utils import user_signup_preparation


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signin')
async def login(
    user: AuthUser,
    uow: UOWDep
) -> dict:
    """
    User authorization in the application.

    Requireds:
        - user data.
    """
    user: User = await UserService.authenticate(uow, user)
    return await jwt_service.write(user)


@router.post(
    '/signup',
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def registering_user(
    user_schema: UserCreateSchema,
    uow: UOWDep,
    code: Optional[str] = None
):
    """
    Registers a new user in the application.

    Requireds:
        - user data.
    ---
    Optional:
        - query parameter: code -- token for invited user.
    """
    if not code:
        user_data: dict = await user_signup_preparation(
            uow,
            user_schema.model_dump()
        )
        created_user: User = await UserService.create(uow, user_data)
        return created_user.to_pydantic_schema()

    details: dict = await RedisClient.get_cache(code)
    created_user: User = await UserService.create_invited_user(
        uow,
        details,
        user_schema.model_dump()
    )
    await RedisClient.remove(code)
    return created_user.to_pydantic_schema()
