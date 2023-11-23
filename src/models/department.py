from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.api.v1.schemas.response.department import DepartmentResponseSchema
from src.models.bases import Base
from src.models.mixins.common import GenericFieldsMixin
from src.models.mixins.organizations import RefOrganizationMixin
from src.models.mixins.users import RefUserMixin

if TYPE_CHECKING:
    from src.models.employee import Employee


class Department(RefUserMixin, GenericFieldsMixin, RefOrganizationMixin, Base):

    __tablename__ = 'department'
    _organization_back_populates = 'departments'

    employees: Mapped[list['Employee']] = relationship(
        back_populates='department',
        lazy='selectin'
    )

    def to_pydantic_schema(
        self,
    ) -> DepartmentResponseSchema:
        return DepartmentResponseSchema(
            id=self.id,
            created_by=self.user_id,
            name=self.name,
            description=self.description,
            organization_id=self.organization_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            employees=[
                emp.to_pydantic_schema()
                for emp in self.employees
            ]
        )
