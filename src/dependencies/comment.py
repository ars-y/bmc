from typing import Annotated

from fastapi import Depends

from src.dependencies.permissions import get_department_contributor
from src.exceptions.auth import PermissionDenied
from src.models import Employee, Task
from src.schemas.request.comment import CommentCreateSchema
from src.services import task as task_db


async def get_comment_create_data(
    task_id: int,
    comment_schema: CommentCreateSchema,
    author: Annotated[Employee, Depends(get_department_contributor)]
) -> dict:
    """Returns data for creating a comment."""
    task: Task = await task_db.service.get(task_id)
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
