from datetime import datetime

from pydantic import BaseModel

from src.api.v1.schemas.response.employee import EmployeeResponseSchema


class MeetingResponseSchema(BaseModel):

    id: int
    created_by: int
    description: str
    start_at: datetime
    end_at: datetime
    created_at: datetime
    updated_at: datetime
    employees: list[EmployeeResponseSchema] = []


class MeetingWithWithOccupiedEmployees(MeetingResponseSchema):

    occupied_employees: list[EmployeeResponseSchema] = []
