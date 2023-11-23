from src.enums.role import RoleEnum
from src.models import Organization, Role, User
from src.services.bases import StorageBaseService, UOWType


class OrganizationService(StorageBaseService):

    _repository = 'organization_repository'

    @classmethod
    async def create_with_employee(
        cls,
        uow: type[UOWType],
        user: User,
        organization_data: dict
    ) -> Organization:
        role_repo: str = 'role_repository'
        emp_repo: str = 'employee_repository'

        async with uow:
            organization: Organization = (
                await uow.__dict__[cls._repository]
                .create(organization_data)
            )
            role: Role = await uow.__dict__[role_repo].get_by_filters(
                name=RoleEnum.ADMIN.value
            )
            employee_data: dict = {
                'organization_id': organization.id,
                'user_id': user.id,
                'role_id': role.id
            }
            await uow.__dict__[emp_repo].create(employee_data)
            return await uow.__dict__[cls._repository].get(organization.id)
