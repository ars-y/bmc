from pydantic import BaseModel, EmailStr


class UserResponseSchema(BaseModel):

    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    role_id: int
