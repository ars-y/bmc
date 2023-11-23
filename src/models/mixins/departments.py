from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

from src.models import Department


class RefDepartmentMixin:
    """
    Declared attrs:

        - `department_id`: Foreign Key to Department id
        that can be nullable (default -- False);
        - `department`: relationship to Department table
        with back populates (default -- None) and lazy select IN loading.
    """

    _department_back_populates: Optional[str] = None
    _department_id_nullable: bool = False

    @declared_attr
    def department_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey('department.id'),
            nullable=cls._department_id_nullable
        )

    @declared_attr
    def department(cls) -> Mapped[Department]:
        return relationship(
            Department,
            back_populates=cls._department_back_populates,
            lazy='selectin'
        )
