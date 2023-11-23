from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from src.api.v1.schemas.response.employee import EmployeeResponseSchema
from src.models.bases import Base
from src.models.mixins.sets import GenericUDORMixin

if TYPE_CHECKING:
    from src.models.meeting import Meeting


class Employee(GenericUDORMixin, Base):

    __tablename__ = 'employee'
    _organization_back_populates = 'employees'
    _department_back_populates = 'employees'
    _department_id_nullable = True

    meetings: Mapped[list['Meeting']] = relationship(
        secondary='employee_meeting',
        back_populates='employees',
        lazy='selectin'
    )

    def to_pydantic_schema(self) -> EmployeeResponseSchema:
        return EmployeeResponseSchema(
            id=self.id,
            organization_id=self.organization_id,
            department_id=self.department_id,
            user_id=self.user_id,
            role_id=self.role_id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
