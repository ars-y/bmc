from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.dependencies import (
    get_current_task_with_update_data,
    get_comment_create_data,
    get_current_task,
    get_task_create_data,
    get_task_score_create_data,
    get_task_to_delete,
    query_params_get_list
)
from src.models import Comment, Score, Task
from src.schemas.request.task import TaskEditStatusSchema
from src.schemas.response.comment import CommentResponseSchema
from src.schemas.response.score import ScoreResponseSchema
from src.schemas.response.task import TaskResponseSchema
from src.services import (
    comment as comment_db,
    score as score_db,
    task as task_db
)
from src.services.utils import recieve_selection_data


router = APIRouter(prefix='/task', tags=['Task'])


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponseSchema)
async def create_task(
    task_data: Annotated[dict, Depends(get_task_create_data)]
):
    """
    Creating task.

    Requireds:
        - create task data;
        - authenticated by token;
        - permission to create tasks in department.
    """
    task: Task = await task_db.service.create(task_data)
    return task.to_pydantic_schema()


@router.patch(
    '/{task_id}',
    response_model=TaskResponseSchema
)
async def change_task_status(
    task_data: Annotated[
        tuple[TaskEditStatusSchema, Task],
        Depends(get_current_task_with_update_data)
    ]
):
    """
    Update task status.

    Requireds:
        - task status;
        - task ID;
        - authenticated by token;
        - permission to edit tasks in department.
    """
    task_schema, task = task_data
    task: Task = await task_db.service.update(
        task.id,
        {'status': task_schema.status}
    )
    return task.to_pydantic_schema()


@router.get(
    '/{task_id}/comments',
    response_model=list[CommentResponseSchema]
)
async def get_task_comments(
    task: Annotated[Task, Depends(get_current_task)],
    query_params: Annotated[dict, Depends(query_params_get_list)]
):
    """
    Getting all comments for task.

    Requireds:
        - task ID;
        - authenticated by token;
        - permission to view comments for current task.
    ---
    Optional query parameters:
        - `offset`: number of skip;
        - `limit`: limit the number of results;
        - `sort_by`: sort by field name;
        - `sort`: ascending or descending.
    """
    data: dict = recieve_selection_data('task_id', task.id, query_params)
    comments: list[Comment] = await comment_db.service.get_all(data)

    return [
        comment.to_pydantic_schema()
        for comment in comments
    ]


@router.post(
    '/{task_id}/comments',
    response_model=CommentResponseSchema
)
async def add_task_comment(
    comment_data: Annotated[dict, Depends(get_comment_create_data)]
):
    """
    Create comment to task.

    Requireds:
        - task ID;
        - comment data;
        - authenticated by token;
        - permission to create comments for task.
    """
    comment: Comment = await comment_db.service.create(comment_data)
    return comment.to_pydantic_schema()


@router.post(
    '/{task_id}/score',
    status_code=status.HTTP_201_CREATED,
    response_model=ScoreResponseSchema
)
async def evaluate_task(
    score_data: Annotated[dict, Depends(get_task_score_create_data)]
):
    """
    Evaluating the task.

    Requireds:
        - task ID;
        - score data;
        - authenticated by token;
        - permission to evaluate the specified task.
    """
    score: Score = await score_db.service.create(score_data)
    return score.to_pydantic_data()


@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task: Annotated[Task, Depends(get_task_to_delete)]
) -> None:
    """
    Delete task.
    Not available for tasks with status - `Done`.

    Requireds:
        - task ID;
        - authenticated by token;
        - permission to delete task.
    """
    await task_db.service.delete(task.id)
    return
