from typing import Annotated

from fastapi import Depends

from src.dependencies.organizations import get_current_organization
from src.dependencies.permissions import get_department_contributor
from src.exceptions.bases import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.models import Department, Employee, Organization
from src.services import department as dept_db


async def get_department_for_admin(
    dept_id: int,
    organization_data: Annotated[dict, Depends(get_current_organization)]
) -> dict:
    """
    Returns a dict with an department db object
    and the current admin which depends on the current organization.
    """
    organization: Organization = organization_data.get('organization')
    department: Department = await dept_db.service.get(dept_id)
    if not department:
        raise ObjectNotFound()

    if department.organization_id != organization.id:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'The department does not belong to the organization'
        }
        raise PermissionDenied(extra_msg=error_info)

    return {
        'department': department,
        'current_user': organization_data.get('current_user')
    }


async def get_department_for_employee(
    dept_id: int,
    org_id: int,
    employee: Annotated[Employee, Depends(get_department_contributor)]
) -> Department:
    """Returns a department that depends on the current contributor."""
    department: Department = await dept_db.service.get(dept_id)
    if not department:
        raise ObjectNotFound()

    if (
        department.organization_id != org_id
        or employee.department_id != department.id
        or employee.organization_id != org_id
    ):
        raise PermissionDenied()

    return department
