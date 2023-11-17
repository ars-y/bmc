from typing import Union

from src.cache.redis import RedisClient
from src.enums.role import RoleEnum
from src.enums.status import STATUS_STATES
from src.exceptions.auth import InvationCodeError
from src.exceptions.db import ObjectNotFound
from src.models.organization import Organization
from src.models.role import Role
from src.models.user import User
from src.services import (
    employee as emp_db,
    organization as org_db,
    role as role_db,
    user as user_db
)

from src.utils.security import pwd_guard


async def user_signup_preparation(
    user_data: dict,
    *,
    role_name: str = RoleEnum.ADMIN.value
) -> dict:
    """
    Adds the necessary data to the user dict.

    Args:
        - `user data` -- dict with user data;
        - `role_name` -- role name keyword (default 'admin').
    """
    role: Role = await role_db.service.get_by_filters(name=role_name)

    if not role:
        error_info: dict = {
            'reason': 'Object not found',
            'description': 'Before creating a user you need to create roles'
        }
        raise ObjectNotFound(extra_msg=error_info)

    password: str = user_data.pop('password')
    user_data.update(
        hashed_password=pwd_guard.get_password_hash(password),
        is_active=True,
        is_superuser=False,
        role_id=role.id
    )
    return user_data


async def create_invited_user(code: str, user_data: dict) -> User:
    """
    Creating a User, Employee
    and bound the employee to the invited organization.

    Args:
        - `code` -- invitation token;
        - `user data` -- dict with data to create User.
    """
    details: dict = await RedisClient.get_cache(code)
    if not details:
        raise InvationCodeError()

    org_id: int = details.get('organization').get('id')
    organization: Organization = await org_db.service.get(org_id)

    if not organization:
        error_info: dict = {
            'reason': 'Object not found',
            'description': (
                'The organization you were invited to has been deleted '
                'or never existed'
            )
        }
        raise ObjectNotFound(extra_msg=error_info)

    user_data: dict = await user_signup_preparation(
        user_data,
        role_name=RoleEnum.VIEWER.value
    )
    user: User = await user_db.service.create(user_data)
    employee_data: dict = {
        'user_id': user.id,
        'organization_id': organization.id,
        'role_id': user.role_id
    }
    await emp_db.service.create(employee_data)
    await RedisClient.remove(code)
    return user


def convert_status(status_name: str) -> int:
    """Convert status from string type to integer."""
    for st in STATUS_STATES:
        if STATUS_STATES[st].name.lower() == status_name.lower():
            return STATUS_STATES[st].value


def recieve_selection_data(
    field_name: str,
    field_value: Union[int, str],
    params: dict
) -> dict:
    """Returns dict with filters for selecting data from database."""
    return {
        'filters': {
            field_name: field_value,
        },
        'offset': params.get('offset'),
        'limit': params.get('limit'),
        'order': params.get('order'),
        'order_by_field': params.get('order_by_field')
    }
