from src.api.v1.dependencies.permissions import get_department_manager
from src.api.v1.schemas.request.score import ScoreCreateSchema
from src.enums.status import StatusEnum
from src.exceptions.auth import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.models import Employee, Task
from src.services import TaskService
from src.units.unit_of_work import UnitOfWork


async def get_task_score_create_data(
    task_id: int,
    uow: UnitOfWork,
    token: str,
    score_schema: ScoreCreateSchema
) -> dict:
    """
    Returns data for creating a score.
    Сalculates whether the task performer met the deadline
    """
    author: Employee = await get_department_manager(uow, token)
    task: Task = await TaskService.get(uow, task_id)
    if not task:
        raise ObjectNotFound()

    if task.created_by != author.id:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': (
                'Don\'t have permission to evaluate the specified task'
            )
        }
        raise PermissionDenied(extra_msg=error_info)

    if task.status != StatusEnum.DONE:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'It\'s forbidden to evaluate an uncompleted task'
        }
        raise PermissionDenied(extra_msg=error_info)

    return {
        'employee_id': task.assignee,
        'task_id': task.id,
        'in_time': 1 if task.updated_at < task.deadline else 0,
        'integrity': score_schema.integrity,
        'quality': score_schema.quality
    }
