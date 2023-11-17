from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.background.app import send_email_org_invite
from src.cache.redis import RedisClient
from src.core.constants import INVITE_EXPIRE_SECONDS
from src.dependencies import (
    get_current_admin,
    get_department_for_admin,
    get_department_for_employee,
    get_meeting_create_data,
    get_meeting_delete_data,
    get_meeting_update_data,
    get_current_organization,
    get_department_employee,
    get_organization_employee,
    query_params_get_list,
)
from src.enums.role import RoleEnum
from src.exceptions.db import ObjectNotFound
from src.models import (
    Department,
    Employee,
    Meeting,
    Organization,
    Role,
    User
)
from src.schemas.request import (
    department as dept_schema,
    invite as invite_schema,
    organization as org_schema
)
from src.schemas.response import (
    department as dept_res_schema,
    employee as emp_res_schema,
    meeting as meet_res_schema,
    organization as org_res_schema,

)
from src.services import (
    department as dept_db,
    employee as emp_db,
    meeting as meet_db,
    organization as org_db,
    role as role_db,
    user as user_db
)
from src.services.utils import recieve_selection_data
from src.utils.security import generate_url_token


router = APIRouter(prefix='/org', tags=['Organization'])


@router.get(
    '',
    response_model=list[org_res_schema.OrganizationResponseSchema]
)
async def get_all_organizations(
    user: Annotated[User, Depends(get_current_admin)],
    query_params: Annotated[dict, Depends(query_params_get_list)]
):
    """
    Returns a list of all organizations.

    Requireds:
        - authenticated by token;
        - permission to view organizations.
    ---
    Optional query parameters:
        - `offset`: number of skip;
        - `limit`: limit the number of results;
        - `sort_by`: sort by field name;
        - `sort`: ascending or descending.
    """
    data: dict = recieve_selection_data('user_id', user.id, query_params)
    organizations: list[Organization] = await org_db.service.get_all(data)
    return [
        organization.to_pydantic_schema()
        for organization in organizations
    ]


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=org_res_schema.OrganizationResponseSchema
)
async def create_organization(
    org_schema: org_schema.OrganizationCreateSchema,
    current_user: Annotated[User, Depends(get_current_admin)]
):
    """
    Сreation of an organization.

    Requireds:
        - organization data;
        - authenticated by token;
        - permission to create organization.
    """
    organization_data: dict = org_schema.model_dump()
    organization_data['user_id'] = current_user.id
    organization: Organization = await org_db.service.create(organization_data)
    role: Role = await role_db.service.get_by_filters(
        name=RoleEnum.ADMIN.value
    )
    employee_data: dict = {
        'organization_id': organization.id,
        'user_id': current_user.id,
        'role_id': role.id
    }
    await emp_db.service.create(employee_data)
    return organization.to_pydantic_schema()


@router.post('/{org_id}/invite')
async def create_user_invite(
    invite_schema: invite_schema.InvitionCreateSchema,
    organization_data: Annotated[dict, Depends(get_current_organization)]
):
    """
    Invite user in organization by ID.

    Requireds:
        - organization ID;
        - invitee data;
        - authenticated by token;
        - permission to invite user in current organization.
    """
    organization: Organization = organization_data.get('organization')
    current_user: User = organization_data.get('current_user')
    key: str = generate_url_token()
    invation_details: dict = {
        'invited_by': {
            'id': current_user.id,
            'email': current_user.email,
        },
        'organization': {
            'id': organization.id,
            'name': organization.name,
        },
        'invitee': {
            'email': invite_schema.email,
        }
    }
    await RedisClient.set_cache(key, invation_details, INVITE_EXPIRE_SECONDS)
    invation_details['code'] = key
    send_email_org_invite.delay(invation_details)
    invation_details.pop('code')
    invation_details['status'] = 'Pending'
    return invation_details


@router.patch(
    '/{org_id}',
    response_model=org_res_schema.OrganizationResponseSchema
)
async def update_organization(
    org_schema: org_schema.OrganizationCreateSchema,
    organization_data: Annotated[dict, Depends(get_current_organization)],
):
    """
    Update organization by ID.

    Requireds:
        - organization update data;
        - organization ID;
        - authenticated by token;
        - permission to update organization.
    """
    organization: Organization = organization_data.get('organization')
    org_update_data: dict = org_schema.model_dump()
    organization: Organization = await org_db.service.update(
        organization.id,
        org_update_data
    )
    return organization.to_pydantic_schema()


@router.delete(
    '/{org_id}',
    response_model=org_res_schema.DeleteOrgResponseSchema
)
async def delete_organization(
    organization_data: Annotated[dict, Depends(get_current_organization)]
):
    """
    Delete organization by ID.

    Requireds:
        - organization ID;
        - authenticated by token;
        - permission to delete organization.
    """
    organization: Organization = organization_data.get('organization')
    current_user: User = organization_data.get('current_user')

    await org_db.service.delete(organization.id)

    return org_res_schema.DeleteOrgResponseSchema(
        id=organization.id,
        deleted_by=current_user.id,
        name=organization.name
    )


@router.get(
    '/{org_id}/employees',
    response_model=list[emp_res_schema.EmployeeResponseSchema]
)
async def get_all_employees_in_organization(
    organization_data: Annotated[dict, Depends(get_current_organization)],
    query_params: Annotated[dict, Depends(query_params_get_list)]
):
    """
    Returns list of employees of the organization.

    Requireds:
        - organization ID;
        - authenticated by token;
        - permissions to view employees in organization.
    ---
    Optional query parameters:
        - `offset`: number of skip;
        - `limit`: limit the number of results;
        - `sort_by`: sort by field name;
        - `sort`: ascending or descending.
    """
    organization: Organization = organization_data.get('organization')
    data: dict = recieve_selection_data(
        'organization_id',
        organization.id,
        query_params
    )
    employees: list[Employee] = await emp_db.service.get_all(data)

    return [
        employee.to_pydantic_schema()
        for employee in employees
    ]


@router.post(
    '/{org_id}/employees/remove',
    response_model=emp_res_schema.DismissedEmployeeSchema
)
async def remove_employee_from_organization(
    employee_data: Annotated[dict, Depends(get_organization_employee)]
):
    """
    Removing employee from a organization.
    When an Employee leaves an organization,
    the associated User is not removed from the database.
    It's `is_active` field becomes False.

    Requireds:
        - employee data;
        - organization ID;
        - authenticated by token;
        - permission to remove employee from organization.
    """
    employee: Employee = employee_data.pop('employee')
    await user_db.service.update(employee.user_id, {'is_active': False})

    return emp_res_schema.DismissedEmployeeSchema(
        dismissed_employee=employee.to_pydantic_schema()
    )


@router.get(
    '/{org_id}/department',
    response_model=list[dept_res_schema.DepartmentResponseSchema]
)
async def get_all_departments_in_organization(
    organization_data: Annotated[dict, Depends(get_current_organization)],
    query_params: Annotated[dict, Depends(query_params_get_list)]
):
    """
    Returns all departments of the current organization.

    Requireds:
        - organization ID;
        - authenticated by token;
        - permission to view departments in organization.
    ---
    Optional query parameters:
        - `offset`: number of skip;
        - `limit`: limit the number of results;
        - `sort_by`: sort by field name;
        - `sort`: ascending or descending.
    """
    organization: Organization = organization_data.get('organization')
    data: dict = recieve_selection_data(
        'organization_id',
        organization.id,
        query_params
    )
    departments: list[Department] = await dept_db.service.get_all(data)
    return [
        department.to_pydantic_schema()
        for department in departments
    ]


@router.post(
    '/{org_id}/department',
    status_code=status.HTTP_201_CREATED,
    response_model=dept_res_schema.DepartmentResponseSchema
)
async def create_department(
    dept_schema: dept_schema.DepartmentCreateSchema,
    organization_data: Annotated[dict, Depends(get_current_organization)]
):
    """
    Сreating a department in an organization.

    Requireds:
        - department create data;
        - organization ID;
        - authenticated by token;
        - permission to create department.
    """
    organization: Organization = organization_data.get('organization')
    current_user: User = organization_data.get('current_user')

    dept_data: dict = dept_schema.model_dump()
    dept_data.update(
        user_id=current_user.id,
        organization_id=organization.id
    )
    department: Department = await dept_db.service.create(dept_data)

    return department.to_pydantic_schema()


@router.patch(
    '/{org_id}/department/{dept_id}',
    response_model=dept_res_schema.DepartmentResponseSchema
)
async def update_department(
    dept_schema: dept_schema.DepartmentCreateSchema,
    department_data: Annotated[dict, Depends(get_department_for_admin)]
):
    """
    Updating department in current organization.

    Requireds:
        - department update data;
        - organization ID;
        - department ID;
        - authenticated by token;
        - permission to update department.
    """
    department: Department = department_data.get('department')
    dept_update_data: dict = dept_schema.model_dump()
    department: Department = await dept_db.service.update(
        department.id,
        dept_update_data
    )
    return department.to_pydantic_schema()


@router.delete(
    '/{org_id}/department/{dept_id}',
    response_model=dept_res_schema.DeleteDeptResponseSchema
)
async def delete_department(
    department_data: Annotated[dict, Depends(get_department_for_admin)]
):
    """
    Deleting department by ID.

    Requireds:
        - organization ID;
        - department ID;
        - authenticated by token;
        - permission to delete department.
    """
    department: Department = department_data.get('department')
    current_user: User = department_data.get('current_user')
    department: Department = await dept_db.service.delete(department.id)

    return dept_res_schema.DeleteDeptResponseSchema(
        id=department.id,
        deleted_by=current_user.id,
        name=department.name
    )


@router.get(
    '/{org_id}/department/{dept_id}/employees',
    response_model=list[emp_res_schema.EmployeeResponseSchema]
)
async def get_all_employees_in_department(
    department: Annotated[Department, Depends(get_department_for_employee)],
    query_params: Annotated[dict, Depends(query_params_get_list)]
):
    """
    Returns list of department employees.

    Requireds:
        - organization ID;
        - department ID;
        - authenticated by token;
        - permissions to view employees in department.
    ---
    Optional query parameters:
        - `offset`: number of skip;
        - `limit`: limit the number of results;
        - `sort_by`: sort by field name;
        - `sort`: ascending or descending.
    """
    data: dict = recieve_selection_data(
        'department_id',
        department.id,
        query_params
    )
    employees: list[Employee] = await emp_db.service.get_all(data)
    return [
        employee.to_pydantic_schema()
        for employee in employees
    ]


@router.post(
    '/{org_id}/department/{dept_id}/employees',
    status_code=status.HTTP_201_CREATED,
    response_model=dept_res_schema.DepartmentResponseSchema
)
async def add_employee_to_department(
    employee_data: Annotated[dict, Depends(get_organization_employee)],
    department_data: Annotated[dict, Depends(get_department_for_admin)]
):
    """
    Add employee to department.
    When adding an employee, his role changes if it's not specified.

    Requireds:
        - employee data;
        - organization ID;
        - department ID;
        - authenticated by token;
        - permission to add employee to a department.
    """
    employee: Employee = employee_data.pop('employee')
    if 'role_id' not in employee_data:
        role: Role = await role_db.service.get_by_filters(
            name=RoleEnum.CONTRIBUTOR.value
        )
        employee_data['role_id'] = role.id

    department: Department = department_data.get('department')
    employee = await emp_db.service.update(
        employee.id,
        {
            'department_id': department.id,
            'role_id': employee_data.get('role_id')
        }
    )
    department: Department = await dept_db.service.get(department.id)

    return department.to_pydantic_schema()


@router.patch(
    '/{org_id}/department/{dept_id}/employees',
    response_model=dept_res_schema.DepartmentResponseSchema
)
async def update_department_employee_role(
    employee_data: Annotated[dict, Depends(get_department_employee)]
):
    """
    Updating employee role in a department.

    Requireds:
        - employee data;
        - organization ID;
        - department ID;
        - authenticated by token;
        - permission to update employees role.
    """
    employee: Employee = employee_data.pop('employee')
    role: Role = await role_db.service.get(employee_data.get('role_id'))
    if not role:
        raise ObjectNotFound()

    employee: Employee = await emp_db.service.update(
        employee.id,
        {'role_id': role.id}
    )
    department: Department = await dept_db.service.get(employee.department_id)
    return department.to_pydantic_schema()


@router.post(
    '/{org_id}/department/{dept_id}/employees/remove',
    response_model=dept_res_schema.DepartmentResponseSchema
)
async def remove_employee_from_department(
    employee_data: Annotated[dict, Depends(get_department_employee)]
):
    """
    Removing employee from a department.
    When employee is removed from a department,
    his role changes to the default role.

    Requireds:
        - employee data;
        - organization ID;
        - department ID;
        - authenticated by token;
        - permission to remove employee from department.
    """
    employee: Employee = employee_data.pop('employee')

    role: Role = await role_db.service.get_by_filters(
        name=RoleEnum.VIEWER.value
    )
    if not role:
        raise ObjectNotFound()

    employee: Employee = await emp_db.service.update(
        employee.id,
        {
            'department_id': None,
            'role_id': role.id
        }
    )
    department: Department = await dept_db.service.get(employee.department_id)
    return department.to_pydantic_schema()


@router.post(
    '/{org_id}/department/{dept_id}/meeting',
    status_code=status.HTTP_201_CREATED,
    response_model=meet_res_schema.MeetingWithWithOccupiedEmployees
)
async def booking_meeting(
    meeting_data: Annotated[dict, Depends(get_meeting_create_data)]
):
    """
    Booking the meeting for department employees.

    Requireds:
        - meeting data;
        - organization ID;
        - department ID;
        - authenticated by token;
        - permission to create meeting.
    """
    unoccupied_employees: list[Employee] = (
        meeting_data.pop('unoccupied_employees')
    )
    occupied_employees: list[Employee] = meeting_data.pop('occupied_employees')

    meeting: Meeting = await meet_db.service.create_meeting_with_employees(
        meeting_data,
        unoccupied_employees
    )

    return meet_res_schema.MeetingWithWithOccupiedEmployees(
        **meeting.to_pydantic_schema().model_dump(),
        occupied_employees=[
            emp.to_pydantic_schema()
            for emp in occupied_employees
        ]
    )


@router.patch(
    '/{org_id}/department/{dept_id}/meeting',
    response_model=meet_res_schema.MeetingWithWithOccupiedEmployees
)
async def update_booking_meeting(
    meeting_data: Annotated[dict, Depends(get_meeting_update_data)]
):
    """
    Meeting booking update.

    Requireds:
        - meeting data;
        - organization ID;
        - department ID;
        - authenticated by token;
        - permission to update meeting.
    """
    unoccupied_employees: list[Employee] = (
        meeting_data.pop('unoccupied_employees')
    )
    occupied_employees: list[Employee] = meeting_data.pop('occupied_employees')
    meeting: Meeting = meeting_data.pop('meeting')

    meeting: Meeting = await meet_db.service.update_meeting_with_employees(
        meeting.id,
        meeting_data,
        unoccupied_employees
    )

    return meet_res_schema.MeetingWithWithOccupiedEmployees(
        **meeting.to_pydantic_schema().model_dump(),
        occupied_employees=[
            emp.to_pydantic_schema()
            for emp in occupied_employees
        ]
    )


@router.post(
    '/{org_id}/department/{dept_id}/meeting/remove',
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_booking_meeting(
    meeting_data: Annotated[dict, Depends(get_meeting_delete_data)]
):
    """
    Removing meeting.

    Requireds:
        - meeting data;
        - organization ID;
        - department ID;
        - authenticated by token;
        - permission to remove meeting.
    """
    meeting: Meeting = meeting_data.get('meeting')
    meeting: Meeting = await meet_db.service.delete(meeting.id)

    return
