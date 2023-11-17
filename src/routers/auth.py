from typing import Optional

from fastapi import APIRouter, status

from src.models import User
from src.schemas.request.auth import AuthUser
from src.schemas.request.user import UserCreateSchema
from src.schemas.response.user import UserResponseSchema
from src.services import (
    user as user_db,
    token
)
from src.services.utils import create_invited_user, user_signup_preparation


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signin')
async def login(user: AuthUser) -> dict:
    """
    User authorization in the application.

    Requireds:
        - user data.
    """
    user: User = await user_db.service.authenticate(user)
    return await token.service.write(user)


@router.post(
    '/signup',
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def registering_user(
    user_schema: UserCreateSchema,
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
            user_schema.model_dump()
        )
        created_user: User = await user_db.service.create(user_data)
        return created_user.to_pydantic_schema()

    created_user: User = await create_invited_user(
        code,
        user_schema.model_dump()
    )
    return created_user.to_pydantic_schema()
