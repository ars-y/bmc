from fastapi import APIRouter, status

from src.api.v1.dependencies import (
    get_task_to_update,
    get_comment_create_data,
    get_current_task,
    get_task_create_data,
    get_task_score_create_data,
    get_task_to_delete
)
from src.api.v1.schemas.request import (
    comment as comment_req_schema,
    score as score_req_schema,
    task as task_req_schema
)
from src.api.v1.schemas.response.comment import CommentResponseSchema
from src.api.v1.schemas.response.score import ScoreResponseSchema
from src.api.v1.schemas.response.task import TaskResponseSchema
from src.dependencies import TokenDeps, QueryParamDeps, UOWDep
from src.models import Comment, Score, Task
from src.services import (
    CommentService,
    ScoreService,
    TaskService
)
from src.services.utils import recieve_selection_data


router = APIRouter(prefix='/task', tags=['Task'])


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponseSchema)
async def create_task(
    uow: UOWDep,
    token: TokenDeps,
    task_schema: task_req_schema.TaskCreateSchema
):
    """
    Creating task.

    Requireds:
        - create task data;
        - authenticated by token;
        - permission to create tasks in department.
    """
    task_create_data: dict = await get_task_create_data(
        uow,
        token,
        task_schema
    )
    task: Task = await TaskService.create(uow, task_create_data)
    return task.to_pydantic_schema()


@router.patch(
    '/{task_id}',
    response_model=TaskResponseSchema
)
async def change_task_status(
    task_id: int,
    uow: UOWDep,
    token: TokenDeps,
    task_schema: task_req_schema.TaskEditStatusSchema
):
    """
    Update task status.

    Requireds:
        - task status;
        - task ID;
        - authenticated by token;
        - permission to edit tasks in department.
    """
    task: Task = await get_task_to_update(task_id, uow, token, task_schema)
    task: Task = await TaskService.update(
        uow,
        task.id,
        {'status': task_schema.status}
    )
    return task.to_pydantic_schema()


@router.get(
    '/{task_id}/comments',
    response_model=list[CommentResponseSchema]
)
async def get_task_comments(
    task_id: int,
    uow: UOWDep,
    token: TokenDeps,
    query_params: QueryParamDeps
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
    task: Task = await get_current_task(task_id, uow, token)
    data: dict = recieve_selection_data('task_id', task.id, query_params)
    comments: list[Comment] = await CommentService.get_all(uow, data)

    return [
        comment.to_pydantic_schema()
        for comment in comments
    ]


@router.post(
    '/{task_id}/comments',
    response_model=CommentResponseSchema
)
async def add_task_comment(
    task_id: int,
    uow: UOWDep,
    token: TokenDeps,
    comment_schema: comment_req_schema.CommentCreateSchema
):
    """
    Create comment to task.

    Requireds:
        - task ID;
        - comment data;
        - authenticated by token;
        - permission to create comments for task.
    """
    comment_create_data: dict = await get_comment_create_data(
        task_id,
        uow,
        token,
        comment_schema
    )
    comment: Comment = await CommentService.create(uow, comment_create_data)
    return comment.to_pydantic_schema()


@router.post(
    '/{task_id}/score',
    status_code=status.HTTP_201_CREATED,
    response_model=ScoreResponseSchema
)
async def evaluate_task(
    task_id: int,
    uow: UOWDep,
    token: TokenDeps,
    score_schema: score_req_schema.ScoreCreateSchema
):
    """
    Evaluating the task.

    Requireds:
        - task ID;
        - score data;
        - authenticated by token;
        - permission to evaluate the specified task.
    """
    score_create_data: dict = await get_task_score_create_data(
        task_id,
        uow,
        token,
        score_schema
    )
    score: Score = await ScoreService.create(uow, score_create_data)
    return score.to_pydantic_data()


@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    uow: UOWDep,
    token: TokenDeps
) -> None:
    """
    Delete task.
    Not available for tasks with status - `Done`.

    Requireds:
        - task ID;
        - authenticated by token;
        - permission to delete task.
    """
    task: Task = await get_task_to_delete(task_id, uow, token)
    await TaskService.delete(uow, task.id)
    return
