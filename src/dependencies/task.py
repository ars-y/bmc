from typing import Annotated

from fastapi import Depends

from src.dependencies.permissions import (
    get_department_manager,
    get_department_contributor
)
from src.enums.role import RoleEnum
from src.enums.status import STATUS_STATES, StatusEnum
from src.exceptions.auth import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.exceptions.request import InvalidData
from src.models import Employee, Task
from src.schemas.request import task as schema
from src.services import (
    employee as emp_db,
    task as task_db
)


async def get_task_create_data(
    task_schema: schema.TaskCreateSchema,
    author: Annotated[Employee, Depends(get_department_manager)]
) -> dict:
    """Returns data for creating a task."""
    assignee: Employee = await emp_db.service.get(task_schema.assignee)
    if not assignee:
        raise ObjectNotFound()

    if assignee.role.name == RoleEnum.VIEWER:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': (
                'The assignee doesn\'t have permission '
                'to execute task.'
            )
        }
        raise PermissionDenied(extra_msg=error_info)

    if author.department_id != assignee.department_id:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'The assignee isn\'t part of the department'
        }
        raise PermissionDenied(extra_msg=error_info)

    task_data: dict = task_schema.model_dump()
    task_data.update(
        created_by=author.id,
        status=StatusEnum.NEW
    )
    return task_data


async def get_current_task_with_update_data(
    task_id: int,
    task_schema: schema.TaskEditStatusSchema,
    employee: Annotated[Employee, Depends(get_department_contributor)]
) -> tuple[schema.TaskEditStatusSchema, Task]:
    """
    Returns a tuple of task schema with task update data and task db object.
    The employee must be the creator or performer of the task.
    """
    if task_schema.status not in STATUS_STATES:
        error_info: dict = {
            'reason': 'Invalid data',
            'description': 'A task status that doesn\'t exist is specified'
        }
        raise InvalidData(extra_msg=error_info)

    task: Task = await task_db.service.get(task_id)
    if not task:
        raise ObjectNotFound()

    if task.status == StatusEnum.DONE:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'It\'s forbidden to change a completed task'
        }
        raise PermissionDenied(extra_msg=error_info)

    if (
        task.created_by != employee.id
        and task.assignee != employee.id
    ):
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'No access rights to the specified task'
        }
        raise PermissionDenied(extra_msg=error_info)

    return task_schema, task


async def get_task_to_delete(
    task_id: int,
    author: Annotated[Employee, Depends(get_department_manager)]
) -> Task:
    """
    Return Task to delete.
    Available for task author and not available for completed tasks.
    """
    task: Task = await task_db.service.get(task_id)
    if not task:
        raise ObjectNotFound()

    if task.created_by != author.id:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': (
                'Don\'t have permission to delete the specified task'
            )
        }
        raise PermissionDenied(extra_msg=error_info)

    if task.status == StatusEnum.DONE:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'It\'s forbidden to change a completed task'
        }
        raise PermissionDenied(extra_msg=error_info)

    return task


async def get_current_task(
    task_id: int,
    employee: Annotated[Employee, Depends(get_department_contributor)]
) -> Task:
    """Returns Task from the current department."""
    task: Task = await task_db.service.get(task_id)
    if not task:
        raise ObjectNotFound()

    if (
        task.author.department_id != employee.department_id
        and task.performer.department_id != employee.department_id
    ):
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'No access rights to the specified task'
        }
        raise PermissionDenied(extra_msg=error_info)

    return task
