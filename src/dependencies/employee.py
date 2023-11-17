from typing import Annotated

from fastapi import Depends

from src.dependencies.departments import get_department_for_admin
from src.dependencies.organizations import get_current_organization
from src.exceptions.auth import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.models import Department, Employee, Organization
from src.schemas.request.employee import EmployeeSchema
from src.services import employee as emp_db


async def get_organization_employee(
    employee_schema: EmployeeSchema,
    organization_data: Annotated[dict, Depends(get_current_organization)]
) -> dict:
    """
    Returns a dict with employee CRUD data and employee db object
    that depends on the current organization.
    """
    employee_data: dict = employee_schema.model_dump()
    employee: Employee = await emp_db.service.get_by_filters(
        user_id=employee_schema.user_id
    )
    if not employee:
        error_info: dict = {
            'reason': 'Object not found',
            'description': 'The specified employee doesn\'t exists'
        }
        raise ObjectNotFound(extra_msg=error_info)

    organization: Organization = organization_data.get('organization')
    if employee.organization_id != organization.id:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': (
                'The specified employee doesn\'t belong to this organization'
            )
        }
        raise PermissionDenied(extra_msg=error_info)

    employee_data.update(employee=employee)
    return employee_data


async def get_department_employee(
    employee_data: Annotated[dict, Depends(get_organization_employee)],
    department: Annotated[Department, Depends(get_department_for_admin)]
) -> dict:
    """
    Returns a dict with employee CRUD data and employee db object
    that depends on the current department.
    """
    employee: Employee = employee_data.get('employee')
    if employee.department_id != department.id:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': (
                'The specified employee doesn\'t belong to this department'
            )
        }
        raise PermissionDenied(extra_msg=error_info)

    return employee_data
