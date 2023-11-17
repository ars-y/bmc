from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.mixins.common import GenericFieldsMixin
from src.mixins.users import RefUserMixin
from src.models.bases import Base
from src.schemas.response.organization import OrganizationResponseSchema

if TYPE_CHECKING:
    from src.models.employee import Employee
    from src.models.department import Department


class Organization(RefUserMixin, GenericFieldsMixin, Base):

    __tablename__ = 'organization'

    employees: Mapped[list['Employee']] = relationship(
        back_populates='organization',
        lazy='selectin'
    )
    departments: Mapped[list['Department']] = relationship(
        back_populates='organization',
        lazy='selectin'
    )

    def to_pydantic_schema(self) -> OrganizationResponseSchema:
        return OrganizationResponseSchema(
            id=self.id,
            created_by=self.user_id,
            name=self.name,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            employees=[
                emp.to_pydantic_schema()
                for emp in self.employees
            ],
            departments=[
                dept.to_pydantic_schema()
                for dept in self.departments
            ]
        )
