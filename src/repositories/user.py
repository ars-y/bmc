from sqlalchemy import insert, select

from src.exceptions import db as db_exc
from src.models import Employee, Organization, User
from src.repositories.bases import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):

    _model = User

    async def create_invited_user(
        self,
        org_id: int,
        user_data: dict
    ) -> User:
        """
        Creating a User, Employee
        and bound the employee to the invited organization.

        Args:
            - `code` -- invitation token;
            - `user data` -- dict with data to create User.
        """
        stmt = select(Organization).where(Organization.id == org_id)
        response = await self._session.execute(stmt)
        organization: Organization = response.scalar_one_or_none()

        if not organization:
            error_info: dict = {
                'reason': 'Object not found',
                'description': (
                    'The organization you were invited to '
                    'has been deleted or never existed'
                )
            }
            raise db_exc.ObjectNotFound(extra_msg=error_info)

        stmt = insert(User).values(**user_data).returning(User)
        response = await self._session.execute(stmt)
        user: User = response.scalar_one_or_none()

        employee_data: dict = {
            'user_id': user.id,
            'organization_id': organization.id,
            'role_id': user.role_id
        }
        employee: Employee = Employee(**employee_data)
        self._session.add(employee)
        return user
