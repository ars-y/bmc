from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.bases import Base


class Employee_Meeting(Base):

    __tablename__ = 'employee_meeting'

    employee_id: Mapped[int] = mapped_column(ForeignKey('employee.id'))
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey('meeting.id', ondelete='CASCADE')
    )
