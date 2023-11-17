from src.models import Employee, Meeting
from src.repositories import meeting
from src.services.bases import StorageBaseService


class MeetingService(StorageBaseService):

    _repository: meeting.MeetingRepository

    async def create_meeting_with_employees(
        self,
        data: dict,
        employees: list[Employee]
    ) -> Meeting:
        """
        Creates a meeting and add employees to it.

        Args:
            - `data`: dict with creation data;
            - `employees`: list with employees to add.
        """
        return await self._repository.create_meeting_with_employees(
            data,
            employees
        )

    async def update_meeting_with_employees(
        self,
        pk: int,
        data: dict,
        employees: list[Employee]
    ) -> Meeting:
        """
        Updates an object in the database by ID.

        Args:
            - `pk`: object ID;
            - `data`: dict with data to update;
            - `employees`: list of employees to replace.
        """
        return await self._repository.update_meeting_with_employees(
            pk,
            data,
            employees
        )


service = MeetingService(meeting.repository)
