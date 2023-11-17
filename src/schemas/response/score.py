from datetime import datetime

from pydantic import BaseModel, Field


class ScoreResponseSchema(BaseModel):

    id: int
    employee_id: int
    task_id: int
    in_time: int = Field(default=0, qe=0, le=1)
    integrity: int = Field(default=1, qe=1, le=10)
    quality: int = Field(default=1, qe=1, le=10)
    created_at: datetime
    updated_at: datetime
