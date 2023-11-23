from typing import Optional

from pydantic import BaseModel


class DepartmentCreateSchema(BaseModel):

    name: str
    description: Optional[str] = None
