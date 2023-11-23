from typing import Optional

from src.exceptions.auth import AuthorizationError
from src.exceptions.db import ObjectNotFound
from src.models.user import User
from src.services import (
    UserService,
    jwt_service
)
from src.units.unit_of_work import UnitOfWork


async def get_current_user(
    uow: UnitOfWork,
    token: str
) -> User:
    """Get current user by valid token."""
    data: dict = await jwt_service.read(token)
    user_id: str = data.get('sub')
    user: Optional[User] = await UserService.get(uow, int(user_id))
    if not user:
        raise ObjectNotFound()

    if not user.is_active:
        raise AuthorizationError()

    return user
