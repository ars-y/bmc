from datetime import datetime
from typing import Annotated

from fastapi import Depends

from src.dependencies.permissions import get_department_manager
from src.exceptions.auth import PermissionDenied
from src.models import Employee, Meeting
from src.schemas.request.meeting import (
    MeetingCreateSchema,
    MeetingDeleteSchema,
    MeetingUpdateSchema
)
from src.services import (
    employee as emp_db,
    meeting as meet_db
)


async def get_meeting_create_data(
    org_id: int,
    dept_id: int,
    meeting_schema: MeetingCreateSchema,
    manager: Annotated[Employee, Depends(get_department_manager)]
) -> dict:
    """
    Recieve data to create meeting.
    The data contains a lists of occupied and
    unoccupied employees on specified datetime.
    """
    _verify_attach_to_org_and_dept(manager, org_id, dept_id)

    data: dict = meeting_schema.model_dump()

    return await _filter_create_update_data(manager, data)


async def get_meeting_update_data(
    org_id: int,
    dept_id: int,
    meeting_schema: MeetingUpdateSchema,
    manager: Annotated[Employee, Depends(get_department_manager)]
) -> dict:
    """
    Recieve data to update meeting.
    The data contains a lists of occupied and
    unoccupied employees on specified datetime.
    """
    _verify_attach_to_org_and_dept(manager, org_id, dept_id)

    data: dict = meeting_schema.model_dump()
    meeting_id: int = data.pop('id')
    meeting: Meeting = await meet_db.service.get(meeting_id)

    _verify_booking_creator(manager, meeting)

    data: dict = await _filter_create_update_data(manager, data)
    data.update(meeting=meeting)

    return data


async def get_meeting_delete_data(
    org_id: int,
    dept_id: int,
    meeting_schema: MeetingDeleteSchema,
    manager: Annotated[Employee, Depends(get_department_manager)]
) -> dict:
    """
    Recieve data to update meeting.
    The data contains a lists of occupied and
    unoccupied employees on specified datetime.
    """
    _verify_attach_to_org_and_dept(manager, org_id, dept_id)

    meeting: Meeting = await meet_db.service.get(meeting_schema.id)
    _verify_booking_creator(manager, meeting)

    return {'meeting': meeting}


async def _filter_create_update_data(manager: Employee, data: dict) -> dict:
    """Filter data to create or update meeting object."""
    employee_ids: list[int] = data.pop('employee_ids')
    employees: list[Employee] = await emp_db.service.get_by_field_contains(
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
        emp for emp in employees if emp
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
    for i, employee in enumerate(employees):
        if manager.department_id != employee.department_id:
            employee[i] = None
            continue

        for meeting in employee.meetings:
            if (
                meeting.start_at < start_at < meeting.end_at
                or meeting.start_at < end_at < meeting.end_at
            ):
                occupied.append(employees[i])
                employees[i] = None
                break


def _verify_attach_to_org_and_dept(
    employee: Employee,
    organization_id: int,
    department_id: int
) -> None:
    """Verifying attachment to organization and department."""
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
