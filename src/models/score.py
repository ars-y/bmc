from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.mixins.task import RefTaskMixin
from src.models.bases import Base
from src.schemas.response.score import ScoreResponseSchema

if TYPE_CHECKING:
    from src.models.task import Task


class Score(RefTaskMixin, Base):

    __tablename__ = 'score'
    _task_is_unique = True

    employee_id: Mapped[int] = mapped_column(ForeignKey('employee.id'))
    in_time: Mapped[int]
    integrity: Mapped[int]
    quality: Mapped[int]

    task: Mapped['Task'] = relationship(
        back_populates='score',
        lazy='selectin'
    )

    def to_pydantic_data(self) -> ScoreResponseSchema:
        return ScoreResponseSchema(
            id=self.id,
            employee_id=self.employee_id,
            task_id=self.task_id,
            in_time=self.in_time,
            integrity=self.integrity,
            quality=self.quality,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
