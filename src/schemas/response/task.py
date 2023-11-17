from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskResponseSchema(BaseModel):

    id: int
    name: str
    description: Optional[str] = None
    created_by: int
    assignee: int
    status: str
    created_at: datetime
    updated_at: datetime
    deadline: datetime


class DeletedTaskResponseSchema(BaseModel):

    id: int
    name: str
    description: Optional[str] = None
    deleted_by: int
    status: str
