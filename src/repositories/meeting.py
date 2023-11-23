from sqlalchemy import insert, select

from src.exceptions.db import ObjectNotFound
from src.models import Employee, Meeting, Employee_Meeting
from src.repositories.bases import SQLAlchemyRepository


class MeetingRepository(SQLAlchemyRepository):

    _model = Meeting

    async def create_meeting_with_employees(
        self,
        data: dict,
        employees: list[Employee]
    ) -> Meeting:
        """Creating meeting with adding employees from list."""
        meeting: Meeting = self._model(**data)
        stmt = insert(self._model).values(**data).returning(self._model)
        response = await self._session.execute(stmt)
        meeting: Meeting = response.scalar_one_or_none()

        if not meeting:
            raise ObjectNotFound()

        for employee in employees:
            data: dict = {
                'meeting_id': meeting.id,
                'employee_id': employee.id
            }
            self._session.add(Employee_Meeting(**data))

        self._session.add(meeting)

        return meeting

    async def update_meeting_with_employees(
        self,
        pk: int,
        data: dict,
        employees: list[Employee]
    ) -> Meeting:
        """Updating meeting with replace employees list."""
        stmt = select(self._model).where(self._model.id == pk)
        response = await self._session.execute(stmt)
        meeting: Meeting = response.scalar_one_or_none()

        if not meeting:
            raise ObjectNotFound()

        meeting.employees.clear()

        meeting: Meeting = await self.update(pk, data)

        if not meeting:
            raise ObjectNotFound()

        for employee in employees:
            stmt = select(Employee).where(Employee.id == employee.id)
            response = await self._session.execute(stmt)
            employee: Employee = response.scalar_one_or_none()
            meeting.employees.append(employee)

        return meeting
