from pydantic import BaseModel, EmailStr


class InvitionCreateSchema(BaseModel):

    email: EmailStr
