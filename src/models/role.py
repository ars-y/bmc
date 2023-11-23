from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.models.bases import Base
from src.models.mixins.common import GenericFieldsMixin

if TYPE_CHECKING:
    from src.models.permission import Permission


class Role(GenericFieldsMixin, Base):

    __tablename__ = 'role'

    permissions: Mapped[list['Permission']] = relationship(
        secondary='role_permission',
        back_populates='roles',
        lazy='selectin'
    )
