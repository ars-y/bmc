from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.mixins.common import GenericFieldsMixin
from src.models.bases import Base

if TYPE_CHECKING:
    from src.models.role import Role


class Permission(GenericFieldsMixin, Base):

    __tablename__ = 'permission'

    roles: Mapped[list['Role']] = relationship(
        secondary='role_permission',
        back_populates='permissions',
        lazy='selectin'
    )
