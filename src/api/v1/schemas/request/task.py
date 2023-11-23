from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskCreateSchema(BaseModel):

    name: str
    description: Optional[str] = None
    assignee: int
    status: Optional[int] = None
    deadline: datetime


class TaskEditStatusSchema(BaseModel):

    status: int
