from pydantic import BaseModel, EmailStr, Field, field_validator

from src.core.constants import PasswordConst
from src.validators.password import password_validator


class AuthUser(BaseModel):

    email: EmailStr
    password: str = Field(
        min_length=PasswordConst.MIN_LEN,
        max_length=PasswordConst.MAX_LEN
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        return password_validator(password)
