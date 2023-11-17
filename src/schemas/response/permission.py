from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.schemas.response.role import RoleResponseSchema


class PermissionResponseSchema(BaseModel):

    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    roles: list[RoleResponseSchema] = []
