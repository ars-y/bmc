from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

from src.models.organization import Organization


class RefOrganizationMixin:
    """
    Declared attrs:

        - `organization_id`: Foreign Key to Organization id;
        - `organization`: relationship to Organization table
        with back populates (default -- None) and lazy select IN loading.
    """

    _organization_back_populates: Optional[str] = None

    @declared_attr
    def organization_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey('organization.id', ondelete='CASCADE'))

    @declared_attr
    def organization(cls) -> Mapped['Organization']:
        return relationship(
            Organization,
            back_populates=cls._organization_back_populates,
            lazy='selectin'
        )
