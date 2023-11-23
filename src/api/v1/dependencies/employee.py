from src.api.v1.dependencies.departments import get_department_for_admin
from src.api.v1.dependencies.organizations import get_current_organization
from src.api.v1.schemas.request.employee import EmployeeSchema
from src.exceptions.auth import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.models import Department, Employee, Organization, User
from src.services import EmployeeService, UserService
from src.units.unit_of_work import UnitOfWork


async def get_organization_employee(
    org_id: int,
    uow: UnitOfWork,
    user: User,
    employee_schema: EmployeeSchema
) -> Employee:
    """
    Returns an employee database object
    that depends on the current organization.
    """
    organization: Organization = (
        await get_current_organization(org_id, uow, user)
    )
    employee: Employee = await EmployeeService.get_by_filters(
        uow,
        user_id=employee_schema.user_id
    )
    if not employee:
        error_info: dict = {
            'reason': 'Object not found',
            'description': 'The specified employee doesn\'t exists'
        }
        raise ObjectNotFound(extra_msg=error_info)

    employee_account: User = await UserService.get(uow, employee.user_id)

    if (
        not employee_account.is_active
        or employee.organization_id != organization.id
    ):
        error_info: dict = {
            'reason': 'Permission denied',
            'description': (
                'The specified employee doesn\'t belong to this organization'
            )
        }
        raise PermissionDenied(extra_msg=error_info)

    return employee


async def get_department_employee(
    org_id: int,
    dept_id: int,
    uow: UnitOfWork,
    user: User,
    employee_schema: EmployeeSchema
) -> Employee:
    """
    Returns an employee db object
    that depends on the current department.
    """
    department: Department = await get_department_for_admin(
        org_id,
        dept_id,
        uow,
        user
    )
    employee: Employee = await get_organization_employee(
        org_id,
        uow,
        user,
        employee_schema
    )
    if employee.department_id != department.id:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': (
                'The specified employee doesn\'t belong to this department'
            )
        }
        raise PermissionDenied(extra_msg=error_info)

    return employee
