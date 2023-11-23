from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.api.v1.schemas.response.employee import EmployeeResponseSchema


class DepartmentResponseSchema(BaseModel):

    id: int
    created_by: int
    name: str
    description: Optional[str] = None
    organization_id: int
    created_at: datetime
    updated_at: datetime
    employees: list[EmployeeResponseSchema] = []


class DeleteDeptResponseSchema(BaseModel):

    id: int
    deleted_by: int
    name: str
