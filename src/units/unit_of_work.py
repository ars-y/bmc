from types import TracebackType
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import (
    comment,
    department,
    employee,
    meeting,
    organization,
    permission,
    role_permission,
    role,
    score,
    task,
    user
)
from src.units.base import AbstractBaseUnitOfWork


class UnitOfWork(AbstractBaseUnitOfWork):

    def __init__(self, sessionmaker: Callable[..., AsyncSession]) -> None:
        self._session_factory = sessionmaker

    async def __aenter__(self):
        self._session: AsyncSession = self._session_factory()

        self.comment_repository = comment.CommentRepository(self._session)
        self.department_repository = (
            department.DepartmentRepository(self._session)
        )
        self.employee_repository = employee.EmployeeRepository(self._session)
        self.meeting_repository = meeting.MeetingRepository(self._session)
        self.organization_repository = (
            organization.OrganizationRepository(self._session)
        )
        self.permission_repository = (
            permission.PermissionRepository(self._session)
        )
        self.role_permission_repository = (
            role_permission.RolePermissionRepository(self._session)
        )
        self.role_repository = role.RoleRepository(self._session)
        self.score_repository = score.ScoreRepository(self._session)
        self.task_repository = task.TaskRepository(self._session)
        self.user_repository = user.UserRepository(self._session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType
    ):
        if any((exc_type, exc_val, exc_tb)):
            await self.rollback()
        else:
            await self.commit()

        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
