from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EmployeeResponseSchema(BaseModel):

    id: int
    organization_id: int
    department_id: Optional[int] = None
    user_id: int
    role_id: int
    created_at: datetime
    updated_at: datetime


class DismissedEmployeeSchema(BaseModel):

    dismissed_employee: EmployeeResponseSchema
