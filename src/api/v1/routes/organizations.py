from fastapi import APIRouter, status

from src.api.v1.dependencies import (
    get_current_admin,
    get_department_for_admin,
    get_department_for_employee,
    get_meeting_create_data,
    get_meeting_delete_data,
    get_meeting_update_data,
    get_current_organization,
    get_department_employee,
    get_organization_employee
)
from src.api.v1.schemas.request import (
    department as dept_schema,
    employee as emp_schema,
    invite as invite_schema,
    meeting as meet_schema,
    organization as org_schema
)
from src.api.v1.schemas.response import (
    department as dept_res_schema,
    employee as emp_res_schema,
    meeting as meet_res_schema,
    organization as org_res_schema
)
from src.background.app import send_email_org_invite
from src.cache.redis import RedisClient
from src.core.constants import INVITE_EXPIRE_SECONDS
from src.dependencies import TokenDeps, UOWDep, QueryParamDeps
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
from src.services import (
    DepartmentService,
    EmployeeService,
    MeetingService,
    OrganizationService,
    RoleService,
    UserService
)

from src.services.utils import recieve_selection_data
from src.utils.security import generate_url_token


router = APIRouter(prefix='/org', tags=['Organization'])


@router.get(
    '',
    response_model=list[org_res_schema.OrganizationResponseSchema]
)
async def get_all_organizations(
    uow: UOWDep,
    token: TokenDeps,
    query_params: QueryParamDeps
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
    current_admin: User = await get_current_admin(uow, token)
    data: dict = recieve_selection_data(
        'user_id',
        current_admin.id,
        query_params
    )
    organizations: list[Organization] = (
        await OrganizationService.get_all(uow, data)
    )
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
    uow: UOWDep,
    token: TokenDeps,
):
    """
    Сreation of an organization.

    Requireds:
        - organization data;
        - authenticated by token;
        - permission to create organization.
    """
    current_admin: User = await get_current_admin(uow, token)
    organization_data: dict = org_schema.model_dump()
    organization_data['user_id'] = current_admin.id
    organization: Organization = (
        await OrganizationService.create_with_employee(
            uow,
            current_admin,
            organization_data
        )
    )
    return organization.to_pydantic_schema()


@router.post('/{org_id}/invite')
async def create_user_invite(
    org_id: int,
    uow: UOWDep,
    token: TokenDeps,
    invite_schema: invite_schema.InvitionCreateSchema
):
    """
    Invite user in organization by ID.

    Requireds:
        - organization ID;
        - invitee data;
        - authenticated by token;
        - permission to invite user in current organization.
    """
    current_admin: User = await get_current_admin(uow, token)
    organization: Organization = (
        await get_current_organization(org_id, uow, current_admin)
    )
    key: str = generate_url_token()
    invation_details: dict = {
        'invited_by': {
            'id': current_admin.id,
            'email': current_admin.email,
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
    org_id: int,
    uow: UOWDep,
    token: TokenDeps,
    org_schema: org_schema.OrganizationCreateSchema
):
    """
    Update organization by ID.

    Requireds:
        - organization update data;
        - organization ID;
        - authenticated by token;
        - permission to update organization.
    """
    current_admin: User = await get_current_admin(uow, token)
    organization: Organization = (
        await get_current_organization(org_id, uow, current_admin)
    )
    org_update_data: dict = org_schema.model_dump()
    organization: Organization = await OrganizationService.update(
        uow,
        organization.id,
        org_update_data
    )
    organization: Organization = await OrganizationService.get(
        uow,
        organization.id
    )
    return organization.to_pydantic_schema()


@router.delete(
    '/{org_id}',
    response_model=org_res_schema.DeleteOrgResponseSchema
)
async def delete_organization(
    org_id: int,
    uow: UOWDep,
    token: TokenDeps
):
    """
    Delete organization by ID.

    Requireds:
        - organization ID;
        - authenticated by token;
        - permission to delete organization.
    """
    current_admin: User = await get_current_admin(uow, token)
    organization: Organization = (
        await get_current_organization(org_id, uow, current_admin)
    )

    await OrganizationService.delete(uow, organization.id)

    return org_res_schema.DeleteOrgResponseSchema(
        id=organization.id,
        deleted_by=current_admin.id,
        name=organization.name
    )


@router.get(
    '/{org_id}/employees',
    response_model=list[emp_res_schema.EmployeeResponseSchema]
)
async def get_all_employees_in_organization(
    org_id: int,
    uow: UOWDep,
    token: TokenDeps,
    query_params: QueryParamDeps
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
    current_admin: User = await get_current_admin(uow, token)
    organization: Organization = (
        await get_current_organization(org_id, uow, current_admin)
    )
    data: dict = recieve_selection_data(
        'organization_id',
        organization.id,
        query_params
    )
    employees: list[Employee] = await EmployeeService.get_all(uow, data)

    return [
        employee.to_pydantic_schema()
        for employee in employees
    ]


@router.post(
    '/{org_id}/employees/remove',
    response_model=emp_res_schema.DismissedEmployeeSchema
)
async def remove_employee_from_organization(
    org_id: int,
    uow: UOWDep,
    token: TokenDeps,
    employee_schema: emp_schema.EmployeeSchema
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
    current_admin: User = await get_current_admin(uow, token)
    employee: Employee = await get_organization_employee(
        org_id,
        uow,
        current_admin,
        employee_schema
    )
    await UserService.update(uow, employee.user_id, {'is_active': False})

    return emp_res_schema.DismissedEmployeeSchema(
        dismissed_employee=employee.to_pydantic_schema()
    )


@router.get(
    '/{org_id}/department',
    response_model=list[dept_res_schema.DepartmentResponseSchema]
)
async def get_all_departments_in_organization(
    org_id: int,
    uow: UOWDep,
    token: TokenDeps,
    query_params: QueryParamDeps
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
    current_admin: User = await get_current_admin(uow, token)
    organization: Organization = (
        await get_current_organization(org_id, uow, current_admin)
    )
    data: dict = recieve_selection_data(
        'organization_id',
        organization.id,
        query_params
    )
    departments: list[Department] = await DepartmentService.get_all(uow, data)
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
    org_id: int,
    uow: UOWDep,
    token: TokenDeps,
    dept_schema: dept_schema.DepartmentCreateSchema
):
    """
    Сreating a department in an organization.

    Requireds:
        - department create data;
        - organization ID;
        - authenticated by token;
        - permission to create department.
    """
    current_admin: User = await get_current_admin(uow, token)
    organization: Organization = (
        await get_current_organization(org_id, uow, current_admin)
    )

    dept_data: dict = dept_schema.model_dump()
    dept_data.update(
        user_id=current_admin.id,
        organization_id=organization.id
    )
    department: Department = await DepartmentService.create(uow, dept_data)
    department: Department = await DepartmentService.get(uow, department.id)
    return department.to_pydantic_schema()


@router.patch(
    '/{org_id}/department/{dept_id}',
    response_model=dept_res_schema.DepartmentResponseSchema
)
async def update_department(
    org_id: int,
    dept_id: int,
    uow: UOWDep,
    token: TokenDeps,
    dept_schema: dept_schema.DepartmentCreateSchema
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
    current_admin: User = await get_current_admin(uow, token)
    department: Department = await get_department_for_admin(
        org_id,
        dept_id,
        uow,
        current_admin
    )
    dept_update_data: dict = dept_schema.model_dump()
    department: Department = await DepartmentService.update(
        uow,
        department.id,
        dept_update_data
    )
    department: Department = await DepartmentService.get(uow, department.id)
    return department.to_pydantic_schema()


@router.delete(
    '/{org_id}/department/{dept_id}',
    response_model=dept_res_schema.DeleteDeptResponseSchema
)
async def delete_department(
    org_id: int,
    dept_id: int,
    uow: UOWDep,
    token: TokenDeps
):
    """
    Deleting department by ID.

    Requireds:
        - organization ID;
        - department ID;
        - authenticated by token;
        - permission to delete department.
    """
    current_admin: User = await get_current_admin(uow, token)
    department: Department = await get_department_for_admin(
        org_id,
        dept_id,
        uow,
        current_admin
    )
    department: Department = await DepartmentService.delete(uow, department.id)

    return dept_res_schema.DeleteDeptResponseSchema(
        id=department.id,
        deleted_by=current_admin.id,
        name=department.name
    )


@router.get(
    '/{org_id}/department/{dept_id}/employees',
    response_model=list[emp_res_schema.EmployeeResponseSchema]
)
async def get_all_employees_in_department(
    org_id: int,
    dept_id: int,
    uow: UOWDep,
    token: TokenDeps,
    query_params: QueryParamDeps
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
    department: Department = await get_department_for_employee(
        org_id,
        dept_id,
        uow,
        token
    )
    data: dict = recieve_selection_data(
        'department_id',
        department.id,
        query_params
    )
    employees: list[Employee] = await EmployeeService.get_all(uow, data)
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
    org_id: int,
    dept_id: int,
    uow: UOWDep,
    token: TokenDeps,
    employee_schema: emp_schema.EmployeeSchema
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
    current_admin: User = await get_current_admin(uow, token)
    employee: Employee = await get_organization_employee(
        org_id,
        uow,
        current_admin,
        employee_schema
    )
    if not employee_schema.role_id:
        role: Role = await RoleService.get_by_filters(
            uow,
            name=RoleEnum.CONTRIBUTOR.value
        )
        employee_schema.role_id = role.id

    department: Department = await get_department_for_admin(
        org_id,
        dept_id,
        uow,
        current_admin
    )
    employee = await EmployeeService.update(
        uow,
        employee.id,
        {
            'department_id': department.id,
            'role_id': employee_schema.role_id
        }
    )
    department: Department = await DepartmentService.get(uow, department.id)

    return department.to_pydantic_schema()


@router.patch(
    '/{org_id}/department/{dept_id}/employees',
    response_model=dept_res_schema.DepartmentResponseSchema
)
async def update_department_employee_role(
    org_id: int,
    dept_id: int,
    uow: UOWDep,
    token: TokenDeps,
    employee_schema: emp_schema.EmployeeSchema
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
    current_admin: User = await get_current_admin(uow, token)
    employee: Employee = await get_department_employee(
        org_id,
        dept_id,
        uow,
        current_admin,
        employee_schema
    )
    role: Role = await RoleService.get(uow, employee_schema.role_id)
    if not role:
        raise ObjectNotFound()

    employee: Employee = await EmployeeService.update(
        uow,
        employee.id,
        {'role_id': role.id}
    )
    department: Department = (
        await DepartmentService.get(uow, employee.department_id)
    )

    return department.to_pydantic_schema()


@router.post(
    '/{org_id}/department/{dept_id}/employees/remove',
    response_model=dept_res_schema.DepartmentResponseSchema
)
async def remove_employee_from_department(
    org_id: int,
    dept_id: int,
    uow: UOWDep,
    token: TokenDeps,
    employee_schema: emp_schema.EmployeeSchema
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
    current_admin: User = await get_current_admin(uow, token)
    employee: Employee = await get_department_employee(
        org_id,
        dept_id,
        uow,
        current_admin,
        employee_schema
    )

    role: Role = await RoleService.get_by_filters(
        uow,
        name=RoleEnum.VIEWER.value
    )
    if not role:
        raise ObjectNotFound()

    employee: Employee = await EmployeeService.update(
        uow,
        employee.id,
        {
            'department_id': None,
            'role_id': role.id
        }
    )
    department: Department = (
        await DepartmentService.get(uow, dept_id)
    )

    return department.to_pydantic_schema()


@router.post(
    '/{org_id}/department/{dept_id}/meeting',
    status_code=status.HTTP_201_CREATED,
    response_model=meet_res_schema.MeetingWithWithOccupiedEmployees
)
async def booking_meeting(
    org_id: int,
    dept_id: int,
    uow: UOWDep,
    token: TokenDeps,
    meeting_schema: meet_schema.MeetingCreateSchema
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
    meeting_data: dict = await get_meeting_create_data(
        org_id,
        dept_id,
        uow,
        token,
        meeting_schema
    )
    unoccupied_employees: list[Employee] = (
        meeting_data.pop('unoccupied_employees')
    )
    occupied_employees: list[Employee] = meeting_data.pop('occupied_employees')

    meeting: Meeting = await MeetingService.create_meeting_with_employees(
        uow,
        meeting_data,
        unoccupied_employees
    )
    meeting: Meeting = await MeetingService.get(uow, meeting.id)
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
    org_id: int,
    dept_id: int,
    uow: UOWDep,
    token: TokenDeps,
    meeting_schema: meet_schema.MeetingUpdateSchema
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
    meeting_data: dict = await get_meeting_update_data(
        org_id,
        dept_id,
        uow,
        token,
        meeting_schema
    )
    unoccupied_employees: list[Employee] = (
        meeting_data.pop('unoccupied_employees')
    )
    occupied_employees: list[Employee] = meeting_data.pop('occupied_employees')
    meeting: Meeting = meeting_data.pop('meeting')

    meeting: Meeting = await MeetingService.update_meeting_with_employees(
        uow,
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
    org_id: int,
    dept_id: int,
    uow: UOWDep,
    token: TokenDeps,
    meeting_schema: meet_schema.MeetingDeleteSchema
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
    meeting_data: dict = await get_meeting_delete_data(
        org_id,
        dept_id,
        uow,
        token,
        meeting_schema
    )
    meeting: Meeting = meeting_data.get('meeting')
    meeting: Meeting = await MeetingService.delete(uow, meeting.id)

    return
