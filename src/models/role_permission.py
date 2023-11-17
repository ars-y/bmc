from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.bases import Base


class RolePermission(Base):

    __tablename__ = 'role_permission'
    __table_args__ = (UniqueConstraint('role_id', 'permission_id'), )

    role_id: Mapped[int] = mapped_column(ForeignKey('role.id'))
    permission_id: Mapped[int] = mapped_column(ForeignKey('permission.id'))
