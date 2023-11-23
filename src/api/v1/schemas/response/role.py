from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.api.v1.schemas.response.permission import PermissionResponseSchema


class RoleResponseSchema(BaseModel):

    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    permissions: list[PermissionResponseSchema] = []
