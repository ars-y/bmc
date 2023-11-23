from src.models import Employee, Meeting
from src.services.bases import StorageBaseService, UOWType


class MeetingService(StorageBaseService):

    _repository = 'meeting_repository'

    @classmethod
    async def create_meeting_with_employees(
        cls,
        uow: type[UOWType],
        data: dict,
        employees: list[Employee]
    ) -> Meeting:
        """
        Creates a meeting and add employees to it.

        Args:
            - `data`: dict with creation data;
            - `employees`: list with employees to add.
        """
        async with uow:
            return (
                await uow.__dict__[cls._repository]
                .create_meeting_with_employees(data, employees)
            )

    @classmethod
    async def update_meeting_with_employees(
        cls,
        uow: type[UOWType],
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
        async with uow:
            return (
                await uow.__dict__[cls._repository]
                .update_meeting_with_employees(pk, data, employees)
            )
