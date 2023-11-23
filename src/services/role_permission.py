from src.services.bases import StorageBaseService, UOWType


class RolePermissionService(StorageBaseService):

    _repository = 'role_permission_repository'

    @classmethod
    async def add_permissions_to_role(
        cls,
        uow: type[UOWType],
        role_name: str,
        permissions: list[str]
    ) -> None:
        async with uow:
            await uow.__dict__[cls._repository].add_permissions_to_role(
                role_name,
                permissions
            )
