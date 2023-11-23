from datetime import datetime

from pydantic import BaseModel


class CommentResponseSchema(BaseModel):

    id: int
    created_by: int
    content: str
    task_id: int
    created_at: datetime
    updated_at: datetime
