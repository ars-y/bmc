from typing import Annotated, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.exceptions.auth import AuthorizationError
from src.exceptions.db import ObjectNotFound
from src.models.user import User
from src.services import (
    token as token_db,
    user as user_db
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Get current user by valid token."""
    data: dict = await token_db.service.read(token)
    user_id: str = data.get('sub')
    user: Optional[User] = await user_db.service.get(int(user_id))
    if not user:
        raise ObjectNotFound()

    if not user.is_active:
        raise AuthorizationError()

    return user
