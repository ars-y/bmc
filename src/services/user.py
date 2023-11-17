from typing import Optional

from pydantic import EmailStr

from src.core.constants import ErrorCode
from src.exceptions.auth import AuthorizationError
from src.exceptions.user import InvalidCredentialsError
from src.models.user import User
from src.repositories import user
from src.schemas.request.auth import AuthUser
from src.schemas.request.user import PasswordSchema
from src.services.bases import StorageBaseService
from src.utils.security import pwd_guard


class UserService(StorageBaseService):

    async def get_user_by_email(self, email: EmailStr) -> Optional[User]:
        """Gets the `User` by his `email` if it exists."""
        return await self.get_by_filters(email=email)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Gets the `User` by his `username` if it exists."""
        return await self.get_by_filters(username=username)

    async def authenticate(self, model: AuthUser) -> User:
        """Authenticate the user by credentials."""
        user: Optional[User] = await self.get_user_by_email(model.email)
        if not user:
            raise InvalidCredentialsError(extra_msg=ErrorCode.INVALID_EMAIL)

        if not pwd_guard.verify_password(model.password, user.hashed_password):
            raise InvalidCredentialsError(extra_msg=ErrorCode.INVALID_PASSWORD)

        if not user.is_active:
            raise AuthorizationError()

        return user

    async def change_password(
        self,
        user: User,
        password_data: PasswordSchema
    ) -> User:
        """Changes password for user."""
        if (
            not pwd_guard.verify_password(
                password_data.current_password,
                user.hashed_password
            )
        ):
            raise InvalidCredentialsError(extra_msg=ErrorCode.INVALID_PASSWORD)

        if pwd_guard.verify_password(
            password_data.new_password,
            user.hashed_password
        ):
            raise InvalidCredentialsError(extra_msg=ErrorCode.SAME_PASSWORD)

        new_hashed_password: str = (
            pwd_guard.get_password_hash(password_data.new_password)
        )
        return await self.update(
            user.id,
            {'hashed_password': new_hashed_password}
        )


service = UserService(user.repository)
