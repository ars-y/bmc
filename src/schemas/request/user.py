from pydantic import BaseModel, EmailStr, field_validator

from src.validators.password import password_validator


class UserCreateSchema(BaseModel):

    email: EmailStr
    username: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        return password_validator(password)


class PasswordSchema(BaseModel):

    current_password: str
    new_password: str

    @field_validator('current_password', 'new_password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        return password_validator(password)
