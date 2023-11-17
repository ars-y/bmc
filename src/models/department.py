from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.mixins.common import GenericFieldsMixin
from src.mixins.organizations import RefOrganizationMixin
from src.mixins.users import RefUserMixin
from src.models.bases import Base
from src.schemas.response.department import DepartmentResponseSchema

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
