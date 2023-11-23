from typing import Optional

from pydantic import EmailStr

from src.api.v1.schemas.request.auth import AuthUser
from src.api.v1.schemas.request.user import PasswordSchema
from src.core.constants import ErrorCode
from src.enums.role import RoleEnum
from src.exceptions import (
    auth as auth_exc,
    user as user_exc
)
from src.models import User
from src.services.bases import StorageBaseService, UOWType
from src.services.utils import user_signup_preparation
from src.utils.security import pwd_guard


class UserService(StorageBaseService):

    _repository = 'user_repository'

    @classmethod
    async def get_user_by_email(
        cls,
        uow: type[UOWType],
        email: EmailStr
    ) -> Optional[User]:
        """Gets the `User` by his `email` if it exists."""
        return await cls.get_by_filters(uow, email=email)

    @classmethod
    async def get_user_by_username(
        cls,
        uow: type[UOWType],
        username: str
    ) -> Optional[User]:
        """Gets the `User` by his `username` if it exists."""
        return await cls.get_by_filters(uow, username=username)

    @classmethod
    async def authenticate(cls, uow: type[UOWType], model: AuthUser) -> User:
        """Authenticate the user by credentials."""
        user: Optional[User] = await cls.get_user_by_email(uow, model.email)
        if not user:
            raise user_exc.InvalidCredentialsError(
                extra_msg=ErrorCode.INVALID_EMAIL
            )

        if not pwd_guard.verify_password(model.password, user.hashed_password):
            raise user_exc.InvalidCredentialsError(
                extra_msg=ErrorCode.INVALID_PASSWORD
            )

        if not user.is_active:
            raise auth_exc.AuthorizationError()

        return user

    @classmethod
    async def change_password(
        cls,
        uow: type[UOWType],
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
            raise user_exc.InvalidCredentialsError(
                extra_msg=ErrorCode.INVALID_PASSWORD
            )

        if pwd_guard.verify_password(
            password_data.new_password,
            user.hashed_password
        ):
            raise user_exc.InvalidCredentialsError(
                extra_msg=ErrorCode.SAME_PASSWORD
            )

        new_hashed_password: str = (
            pwd_guard.get_password_hash(password_data.new_password)
        )
        return await cls.update(
            uow,
            user.id,
            {'hashed_password': new_hashed_password}
        )

    @classmethod
    async def create_invited_user(
        cls,
        uow: type[UOWType],
        details: dict,
        user_data: dict
    ) -> User:
        """
        Creating a User, Employee
        and bound the employee to the invited organization.

        Args:
            - `code` -- invitation token;
            - `user data` -- dict with data to create User.
        """
        async with uow:
            if not details:
                raise auth_exc.InvationCodeError()

            org_id: int = details.get('organization').get('id')

            user_data: dict = await user_signup_preparation(
                uow,
                user_data,
                role_name=RoleEnum.VIEWER.value
            )
            user: User = (
                await uow.__dict__[cls._repository]
                .create_invited_user(org_id, user_data)
            )
            return user
