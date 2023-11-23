from pydantic import BaseModel

from src.api.v1.schemas.response.score import ScoreResponseSchema
from src.api.v1.schemas.response.task import TaskResponseSchema


class TaskWithScore(BaseModel):

    task: TaskResponseSchema
    score: ScoreResponseSchema


class ScoreWithTasks(BaseModel):

    average_score: float
    tasks: list[TaskWithScore]
