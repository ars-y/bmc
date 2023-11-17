from typing import Annotated, Optional

from fastapi import APIRouter, Depends

from src.dependencies import get_current_user, query_params_get_list
from src.enums.role import RoleEnum
from src.models import (
    Employee,
    Score,
    Task,
    User
)
from src.schemas.request.user import PasswordSchema
from src.schemas.response.task_score import TaskWithScore, ScoreWithTasks
from src.schemas.response.task import TaskResponseSchema
from src.services import (
    employee as emp_db,
    score as score_db,
    task as task_db,
    token,
    user as user_db
)
from src.services.utils import convert_status, recieve_selection_data


router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/me')
async def read_current_user(user: Annotated[User, Depends(get_current_user)]):
    """
    Returns information about the current user.

    Requireds:
        - authenticated by token.
    """
    employee: Employee = await emp_db.service.get_by_filters(user_id=user.id)
    if not employee:
        return user.to_pydantic_schema()

    return employee.to_pydantic_schema()


@router.post('/change-password')
async def change_password(
    password_schema: PasswordSchema,
    user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """
    Changing the current user password.

    Requireds:
        - password data;
        - authenticated by token.
    """
    user: User = await user_db.service.change_password(
        user,
        password_schema
    )
    return await token.service.write(user)


@router.get(
    '/tasks',
    response_model=list[TaskResponseSchema]
)
async def get_employee_tasks(
    user: Annotated[User, Depends(get_current_user)],
    query_params: Annotated[dict, Depends(query_params_get_list)],
    status: Optional[str] = None
):
    """
    Receives a list of tasks for a specific employee.

    Requireds:
        - authenticated by token.
    ---
    Optional query parameters:
        - `offset`: number of skip;
        - `limit`: limit the number of results;
        - `sort_by`: sort by field name;
        - `sort`: ascending or descending;
        - `status`: task status in `new`, `in_progres` or `done`.
    """
    employee: Employee = await emp_db.service.get_by_filters(user_id=user.id)
    if employee.role.name == RoleEnum.OWNER:
        field: str = 'created_by'
    else:
        field: str = 'assignee'

    data: dict = recieve_selection_data(field, employee.id, query_params)
    if status:
        data['filters']['status'] = convert_status(status)

    tasks: list[Task] = await task_db.service.get_all(data)

    return [
        task.to_pydantic_schema()
        for task in tasks
    ]


@router.get(
    '/scores',
    response_model=ScoreWithTasks
)
async def get_employee_scores(
    user: Annotated[User, Depends(get_current_user)],
    query_params: Annotated[dict, Depends(query_params_get_list)]
):
    """
    Receives a list of scores for a specific employee.

    Requireds:
        - authenticated by token.
    ---
    Optional query parameters:
        - `offset`: number of skip;
        - `limit`: limit the number of results;
        - `sort_by`: sort by field name;
        - `sort`: ascending or descending.
    """
    employee: Employee = await emp_db.service.get_by_filters(user_id=user.id)
    data: dict = recieve_selection_data(
        'employee_id',
        employee.id,
        query_params
    )
    scores: list[Score] = await score_db.service.get_all(data)
    avg_score: float = 0.0

    if not scores:
        return ScoreWithTasks(average_score=avg_score, tasks=[])

    total: int = 0
    task_ids: list = []
    for score in scores:
        total += score.in_time + score.integrity + score.quality
        task_ids.append(score.task_id)

    avg_score = total / len(scores)

    return ScoreWithTasks(
        average_score=avg_score,
        tasks=[
            TaskWithScore(
                task=score.task.to_pydantic_schema(),
                score=score.task.score.to_pydantic_data()
            )
            for score in scores
        ]
    )
