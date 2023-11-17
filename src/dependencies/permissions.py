from typing import Annotated

from fastapi import Depends

from src.dependencies.auth import get_current_user
from src.enums.permission import (
    CONTRIBUTOR_PERMISSIONS,
    MANAGER_PERMISSIONS,
    PermissionEnum
)
from src.enums.role import RoleEnum
from src.exceptions.bases import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.models import Employee, User
from src.services import employee as emp_db


async def get_current_superuser(
    user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Gets user with superuser permission."""
    if not user.is_superuser:
        raise PermissionDenied()

    return user


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Gets user with admin role."""
    if user.role.name != RoleEnum.ADMIN:
        raise PermissionDenied()

    return user


async def get_department_manager(
    user: Annotated[User, Depends(get_current_user)]
) -> Employee:
    """
    Returns department employee with next permissions:
        - create;
        - edit;
        - delete;
        - read.
    """
    return await _get_employee_with_permissions(user, MANAGER_PERMISSIONS)


async def get_department_contributor(
    user: Annotated[User, Depends(get_current_user)]
) -> Employee:
    """
    Returns department employee with next permissions:
        - create;
        - edit;
        - read.
    """
    return await _get_employee_with_permissions(user, CONTRIBUTOR_PERMISSIONS)


async def _get_employee_with_permissions(
    user: User,
    necessary_permissions: tuple[PermissionEnum]
) -> Employee:
    employee: Employee = await emp_db.service.get_by_filters(user_id=user.id)

    if not employee:
        error_info: dict = {
            'reason': 'Object not found',
            'description': 'The specified employee doesn\'t exists'
        }
        raise ObjectNotFound(extra_msg=error_info)

    available_permissions: set = set(
        perm.name for perm in employee.role.permissions
    )

    for permission in necessary_permissions:
        if permission not in available_permissions:
            raise PermissionDenied()

    return employee
