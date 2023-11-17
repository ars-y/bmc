from src.db.sessions import get_session
from src.exceptions.db import ObjectNotFound
from src.models import Employee, Meeting
from src.repositories.bases import SQLAlchemyRepository


class MeetingRepository(SQLAlchemyRepository):

    _model: Meeting

    async def create_meeting_with_employees(
        self,
        data: dict,
        employees: list[Employee]
    ) -> Meeting:
        """Creating meeting with adding employees from list."""
        async with self._session() as session:
            try:
                meeting: Meeting = self._model(**data)
                for employee in employees:
                    meeting.employees.append(employee)

                session.add(meeting)
                await session.commit()
            except Exception as exc:
                await session.rollback()
                raise Exception(exc)

            await session.refresh(meeting)
            return meeting

    async def update_meeting_with_employees(
        self,
        pk: int,
        data: dict,
        employees: list[Employee]
    ) -> Meeting:
        """Updating meeting with replace employees list."""
        async with self._session() as session:
            meeting: Meeting = await self.get(pk)

            if not meeting:
                raise ObjectNotFound()

            meeting.employees.clear()
            await session.commit()

            meeting: Meeting = await self.update(pk, data)
            meeting.employees = employees
            await session.commit()

            return meeting


repository = MeetingRepository(Meeting, get_session)
