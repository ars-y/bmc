from src.repositories import role_permission
from src.services.bases import StorageBaseService


class RolePermissionService(StorageBaseService):

    _repository: role_permission.RolePermissionRepository

    async def add_permissions_to_role(
        self,
        role_name: str,
        permissions: list[str]
    ) -> None:
        await self._repository.add_permissions_to_role(
            role_name,
            permissions
        )


service = RolePermissionService(role_permission.repository)
