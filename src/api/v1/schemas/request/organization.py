from typing import Optional

from pydantic import BaseModel


class OrganizationCreateSchema(BaseModel):

    name: str
    description: Optional[str] = None
