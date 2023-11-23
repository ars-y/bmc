from src.api.v1.dependencies.permissions import get_department_contributor
from src.api.v1.schemas.request.comment import CommentCreateSchema
from src.exceptions.auth import PermissionDenied
from src.models import Employee, Task
from src.services import TaskService
from src.units.unit_of_work import UnitOfWork


async def get_comment_create_data(
    task_id: int,
    uow: UnitOfWork,
    token: str,
    comment_schema: CommentCreateSchema
) -> dict:
    """Returns data for creating a comment."""
    author: Employee = await get_department_contributor(uow, token)
    task: Task = await TaskService.get(uow, task_id)
    if (
        author.department_id != task.author.department_id
        and author.department_id != task.performer.department_id
    ):
        error_info: dict = {
            'reason': 'Permission denied',
            'description': (
                'It\'s forbidden to comment on '
                'the tasks of other departments.'
            )
        }
        raise PermissionDenied(extra_msg=error_info)

    comment_data: dict = comment_schema.model_dump()
    comment_data.update(
        created_by=author.id,
        task_id=task.id
    )
    return comment_data
