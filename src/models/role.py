from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.mixins.common import GenericFieldsMixin
from src.models.bases import Base

if TYPE_CHECKING:
    from src.models.permission import Permission


class Role(GenericFieldsMixin, Base):

    __tablename__ = 'role'

    permissions: Mapped[list['Permission']] = relationship(
        secondary='role_permission',
        back_populates='roles',
        lazy='selectin'
    )
