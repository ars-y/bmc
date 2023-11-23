from typing import Optional

from fastapi import APIRouter

from src.api.v1.dependencies import get_current_user
from src.api.v1.schemas.request.user import PasswordSchema
from src.api.v1.schemas.response.task_score import (
    TaskWithScore,
    ScoreWithTasks
)
from src.api.v1.schemas.response.task import TaskResponseSchema
from src.dependencies import TokenDeps, QueryParamDeps, UOWDep
from src.enums.role import RoleEnum
from src.models import (
    Employee,
    Score,
    Task,
    User
)
from src.services import (
    EmployeeService,
    ScoreService,
    TaskService,
    UserService,
    jwt_service
)
from src.services.utils import convert_status, recieve_selection_data


router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/me')
async def read_current_user(
    uow: UOWDep,
    token: TokenDeps
):
    """
    Returns information about the current user.

    Requireds:
        - authenticated by token.
    """
    user: User = await get_current_user(uow, token)
    employee: Employee = await EmployeeService.get_by_filters(
        uow,
        user_id=user.id
    )
    if not employee:
        return user.to_pydantic_schema()

    return employee.to_pydantic_schema()


@router.post('/change-password')
async def change_password(
    uow: UOWDep,
    token: TokenDeps,
    password_schema: PasswordSchema
) -> dict:
    """
    Changing the current user password.

    Requireds:
        - password data;
        - authenticated by token.
    """
    user: User = await get_current_user(uow, token)
    user: User = await UserService.change_password(
        uow,
        user,
        password_schema
    )
    return await jwt_service.write(user)


@router.get(
    '/tasks',
    response_model=list[TaskResponseSchema]
)
async def get_employee_tasks(
    uow: UOWDep,
    token: TokenDeps,
    query_params: QueryParamDeps,
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
    user: User = await get_current_user(uow, token)
    employee: Employee = await EmployeeService.get_by_filters(
        uow,
        user_id=user.id
    )
    if employee.role.name == RoleEnum.OWNER:
        field: str = 'created_by'
    else:
        field: str = 'assignee'

    data: dict = recieve_selection_data(field, employee.id, query_params)
    if status:
        data['filters']['status'] = convert_status(status)

    tasks: list[Task] = await TaskService.get_all(uow, data)

    return [
        task.to_pydantic_schema()
        for task in tasks
    ]


@router.get(
    '/scores',
    response_model=ScoreWithTasks
)
async def get_employee_scores(
    uow: UOWDep,
    token: TokenDeps,
    query_params: QueryParamDeps
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
    user: User = await get_current_user(uow, token)
    employee: Employee = await EmployeeService.get_by_filters(
        uow,
        user_id=user.id
    )
    data: dict = recieve_selection_data(
        'employee_id',
        employee.id,
        query_params
    )
    scores: list[Score] = await ScoreService.get_all(uow, data)
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
