from datetime import datetime

from src.api.v1.dependencies.permissions import get_department_manager
from src.api.v1.schemas.request.meeting import (
    MeetingCreateSchema,
    MeetingDeleteSchema,
    MeetingUpdateSchema
)
from src.enums.role import RoleEnum
from src.exceptions.auth import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.models import Employee, Meeting
from src.services import (
    EmployeeService,
    MeetingService
)
from src.units.unit_of_work import UnitOfWork


async def get_meeting_create_data(
    org_id: int,
    dept_id: int,
    uow: UnitOfWork,
    token: str,
    meeting_schema: MeetingCreateSchema
) -> dict:
    """
    Recieve data to create meeting.
    The data contains a lists of occupied and
    unoccupied employees on specified datetime.
    """
    manager: Employee = await get_department_manager(uow, token)
    _verify_attach_to_org_and_dept(manager, org_id, dept_id)

    data: dict = meeting_schema.model_dump()

    return await _filter_create_update_data(uow, manager, data)


async def get_meeting_update_data(
    org_id: int,
    dept_id: int,
    uow: UnitOfWork,
    token: str,
    meeting_schema: MeetingUpdateSchema
) -> dict:
    """
    Recieve data to update meeting.
    The data contains a lists of occupied and
    unoccupied employees on specified datetime.
    """
    manager: Employee = await get_department_manager(uow, token)
    _verify_attach_to_org_and_dept(manager, org_id, dept_id)

    data: dict = meeting_schema.model_dump()
    meeting_id: int = data.pop('id')
    meeting: Meeting = await MeetingService.get(uow, meeting_id)

    if not meeting:
        raise ObjectNotFound()

    _verify_booking_creator(manager, meeting)

    data: dict = await _filter_create_update_data(uow, manager, data)
    data.update(meeting=meeting)

    return data


async def get_meeting_delete_data(
    org_id: int,
    dept_id: int,
    uow: UnitOfWork,
    token: str,
    meeting_schema: MeetingDeleteSchema,
) -> dict:
    """
    Recieve data to update meeting.
    The data contains a lists of occupied and
    unoccupied employees on specified datetime.
    """
    manager: Employee = await get_department_manager(uow, token)
    _verify_attach_to_org_and_dept(manager, org_id, dept_id)

    meeting: Meeting = await MeetingService.get(uow, meeting_schema.id)

    if not meeting:
        raise ObjectNotFound()

    _verify_booking_creator(manager, meeting)

    return {'meeting': meeting}


async def _filter_create_update_data(
    uow: UnitOfWork,
    manager: Employee,
    data: dict
) -> dict:
    """Filter data to create or update meeting object."""
    employee_ids: list[int] = data.pop('employee_ids')
    employees: list[Employee] = await EmployeeService.get_by_field_contains(
        uow,
        'id',
        employee_ids
    )
    occupied_employees: list[Employee] = []
    _filter_out(
        manager,
        employees,
        occupied_employees,
        data.get('start_at'),
        data.get('end_at')
    )
    unoccupied_employees: list[Employee] = [
        emp for emp in employees if emp not in occupied_employees
    ]
    data.update(
        created_by=manager.id,
        unoccupied_employees=unoccupied_employees,
        occupied_employees=occupied_employees
    )
    return data


def _filter_out(
    manager: Employee,
    employees: list[Employee],
    occupied: list[Employee],
    start_at: datetime,
    end_at: datetime
) -> None:
    """
    Collects a list of occupied employees
    and filters them out from the bulk.
    ---
    It's making in place.
    """
    for employee in employees:
        if (
            manager.role.name != RoleEnum.ADMIN
            and manager.department_id != employee.department_id
        ):
            continue

        for meeting in employee.meetings:
            if (
                meeting.start_at < start_at < meeting.end_at
                or meeting.start_at < end_at < meeting.end_at
            ):
                occupied.append(employee)
                break


def _verify_attach_to_org_and_dept(
    employee: Employee,
    organization_id: int,
    department_id: int
) -> None:
    """Verifying attachment to organization and department."""
    if (
        employee.role.name == RoleEnum.ADMIN
        and employee.organization_id == organization_id
    ):
        return

    if (
        employee.organization_id != organization_id
        or employee.department_id != department_id
    ):
        error_info: dict = {
            'reason': 'Permission denied',
            'description': (
                'No access to the specified organization or department'
            )
        }
        raise PermissionDenied(extra_msg=error_info)


def _verify_booking_creator(employee: Employee, meeting: Meeting) -> None:
    """Verifying that the employee is the meeting creator."""
    if employee.id != meeting.created_by:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'Only the meeting creator can update the data'
        }
        raise PermissionDenied(extra_msg=error_info)
