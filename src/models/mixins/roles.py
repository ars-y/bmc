from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

from src.models.role import Role


class RefRoleMixin:
    """
    Declared attrs:

        - `role_id`: Foreign Key to Role id
        that can be nullable (default -- False);
    """
    _role_back_populates: Optional[str] = None
    _role_id_nullable: bool = False

    @declared_attr
    def role_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey('role.id'),
            nullable=cls._role_id_nullable
        )

    @declared_attr
    def role(cls) -> Mapped[Role]:
        return relationship(
            Role,
            back_populates=cls._role_back_populates,
            lazy='joined'
        )
