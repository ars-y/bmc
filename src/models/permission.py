from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.models.bases import Base
from src.models.mixins.common import GenericFieldsMixin

if TYPE_CHECKING:
    from src.models.role import Role


class Permission(GenericFieldsMixin, Base):

    __tablename__ = 'permission'

    roles: Mapped[list['Role']] = relationship(
        secondary='role_permission',
        back_populates='permissions',
        lazy='selectin'
    )
