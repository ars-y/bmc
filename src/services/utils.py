from typing import Union

from src.enums.role import RoleEnum
from src.enums.status import STATUS_STATES
from src.exceptions.db import ObjectNotFound
from src.models import Role
from src.services import RoleService
from src.units.unit_of_work import UnitOfWork
from src.utils.security import pwd_guard


async def user_signup_preparation(
    uow: UnitOfWork,
    user_data: dict,
    *,
    role_name: str = RoleEnum.ADMIN.value
) -> dict:
    """
    Adds the necessary data to the user dict.

    Args:
        - `uow` -- unit of work;
        - `user data` -- dict with user data;
        - `role_name` -- role name keyword (default 'admin').
    """
    role: Role = await RoleService.get_by_filters(uow, name=role_name)

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
