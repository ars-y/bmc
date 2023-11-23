from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.v1.schemas.response.meeting import MeetingResponseSchema
from src.models.bases import Base

if TYPE_CHECKING:
    from src.models.employee import Employee


class Meeting(Base):

    __tablename__ = 'meeting'

    created_by: Mapped[int] = mapped_column(ForeignKey('employee.id'))
    description: Mapped[str]
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    employees: Mapped[list['Employee']] = relationship(
        secondary='employee_meeting',
        back_populates='meetings',
        lazy='selectin'
    )

    def to_pydantic_schema(self) -> MeetingResponseSchema:
        return MeetingResponseSchema(
            id=self.id,
            created_by=self.created_by,
            description=self.description,
            start_at=self.start_at,
            end_at=self.end_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
            employees=[
                emp.to_pydantic_schema()
                for emp in self.employees
            ]
        )
