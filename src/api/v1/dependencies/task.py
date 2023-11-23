from src.api.v1.dependencies.permissions import (
    get_department_manager,
    get_department_contributor
)
from src.api.v1.schemas.request import task as task_req_schema
from src.enums.role import RoleEnum
from src.enums.status import STATUS_STATES, StatusEnum
from src.exceptions.auth import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.exceptions.request import InvalidData
from src.models import Employee, Task
from src.services import (
    EmployeeService,
    TaskService
)
from src.units.unit_of_work import UnitOfWork


async def get_task_create_data(
    uow: UnitOfWork,
    token: str,
    task_schema: task_req_schema.TaskCreateSchema
) -> dict:
    """Returns data for creating a task."""
    author: Employee = await get_department_manager(uow, token)
    assignee: Employee = await EmployeeService.get(uow, task_schema.assignee)
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


async def get_task_to_update(
    task_id: int,
    uow: UnitOfWork,
    token: str,
    task_schema: task_req_schema.TaskEditStatusSchema,
) -> Task:
    """
    Returns the task db object to update.
    The employee must be the creator or performer of the task.
    """
    contributor: Employee = await get_department_contributor(uow, token)
    if task_schema.status not in STATUS_STATES:
        error_info: dict = {
            'reason': 'Invalid data',
            'description': 'A task status that doesn\'t exist is specified'
        }
        raise InvalidData(extra_msg=error_info)

    task: Task = await TaskService.get(uow, task_id)
    if not task:
        raise ObjectNotFound()

    if task.status == StatusEnum.DONE:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'It\'s forbidden to change a completed task'
        }
        raise PermissionDenied(extra_msg=error_info)

    if (
        task.created_by != contributor.id
        and task.assignee != contributor.id
    ):
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'No access rights to the specified task'
        }
        raise PermissionDenied(extra_msg=error_info)

    return task


async def get_task_to_delete(
    task_id: int,
    uow: UnitOfWork,
    token: str
) -> Task:
    """
    Return Task to delete.
    Available for task author and not available for completed tasks.
    """
    author: Employee = await get_department_manager(uow, token)
    task: Task = await TaskService.get(uow, task_id)
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
    uow: UnitOfWork,
    token: str
) -> Task:
    """Returns Task from the current department."""
    contributor: Employee = await get_department_contributor(uow, token)
    task: Task = await TaskService.get(uow, task_id)
    if not task:
        raise ObjectNotFound()

    if (
        task.author.department_id != contributor.department_id
        and task.performer.department_id != contributor.department_id
    ):
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'No access rights to the specified task'
        }
        raise PermissionDenied(extra_msg=error_info)

    return task
