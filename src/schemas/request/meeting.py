from datetime import datetime

from pydantic import BaseModel


class MeetingCreateSchema(BaseModel):

    description: str
    start_at: datetime
    end_at: datetime
    employee_ids: list[int]


class MeetingUpdateSchema(MeetingCreateSchema):

    id: int


class MeetingDeleteSchema(BaseModel):

    id: int
