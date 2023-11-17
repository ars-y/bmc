from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums.status import STATUS_STATES
from src.mixins.common import GenericFieldsMixin
from src.models.bases import Base
from src.schemas.response.task import TaskResponseSchema

if TYPE_CHECKING:
    from src.models.employee import Employee
    from src.models.score import Score


class Task(GenericFieldsMixin, Base):

    __tablename__ = 'task'
    _name_unique = False

    created_by: Mapped[int] = mapped_column(ForeignKey('employee.id'))
    assignee: Mapped[int] = mapped_column(ForeignKey('employee.id'))
    status: Mapped[int]
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    author: Mapped['Employee'] = relationship(
        foreign_keys='Task.created_by',
        lazy='selectin'
    )
    performer: Mapped['Employee'] = relationship(
        foreign_keys='Task.assignee',
        lazy='selectin'
    )
    score: Mapped['Score'] = relationship(back_populates='task', lazy='joined')

    def to_pydantic_schema(self) -> TaskResponseSchema:
        status: str = STATUS_STATES.get(self.status).name.title()
        return TaskResponseSchema(
            id=self.id,
            name=self.name,
            description=self.description,
            created_by=self.created_by,
            assignee=self.assignee,
            status=status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deadline=self.deadline
        )
