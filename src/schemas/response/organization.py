from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.schemas.response.department import DepartmentResponseSchema
from src.schemas.response.employee import EmployeeResponseSchema


class OrganizationResponseSchema(BaseModel):

    id: int
    created_by: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    employees: list[EmployeeResponseSchema] = []
    departments: list[DepartmentResponseSchema] = []


class DeleteOrgResponseSchema(BaseModel):

    id: int
    deleted_by: int
    name: str
