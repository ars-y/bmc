from src.api.v1.dependencies.organizations import get_current_organization
from src.api.v1.dependencies.permissions import get_department_contributor
from src.enums.role import RoleEnum
from src.exceptions.bases import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.models import Department, Employee, Organization, User
from src.services import DepartmentService
from src.units.unit_of_work import UnitOfWork


async def get_department_for_admin(
    org_id: int,
    dept_id: int,
    uow: UnitOfWork,
    user: User
) -> Department:
    """
    Returns an department db object
    that depends on the current organization.
    """
    organization: Organization = (
        await get_current_organization(org_id, uow, user)
    )
    department: Department = await DepartmentService.get(uow, dept_id)

    if not department:
        raise ObjectNotFound()

    if department.organization_id != organization.id:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'The department does not belong to the organization'
        }
        raise PermissionDenied(extra_msg=error_info)

    return department


async def get_department_for_employee(
    org_id: int,
    dept_id: int,
    uow: UnitOfWork,
    token: str
) -> Department:
    """Returns a department that depends on the current contributor."""
    employee: Employee = await get_department_contributor(uow, token)
    department: Department = await DepartmentService.get(uow, dept_id)

    if not department:
        raise ObjectNotFound()

    if (
        employee.role.name == RoleEnum.ADMIN
        and employee.organization_id == org_id
    ):
        return department

    if (
        department.organization_id != org_id
        or employee.department_id != department.id
        or employee.organization_id != org_id
    ):
        raise PermissionDenied()

    return department
