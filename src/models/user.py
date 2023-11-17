from sqlalchemy.orm import Mapped, mapped_column

from src.mixins.roles import RefRoleMixin
from src.models.bases import Base
from src.schemas.response.user import UserResponseSchema


class User(RefRoleMixin, Base):

    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    def to_pydantic_schema(self) -> UserResponseSchema:
        return UserResponseSchema(
            id=self.id,
            username=self.username,
            email=self.email,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            role_id=self.role_id
        )
