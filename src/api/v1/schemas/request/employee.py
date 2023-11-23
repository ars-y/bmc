from typing import Optional

from pydantic import BaseModel


class EmployeeSchema(BaseModel):

    organization_id: Optional[int] = None
    department_id: Optional[int] = None
    user_id: int
    role_id: Optional[int] = None
