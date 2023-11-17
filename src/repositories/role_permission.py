from src.db.sessions import get_session
from src.exceptions.db import ObjectNotFound
from src.models import Permission, Role, RolePermission
from src.repositories.bases import SQLAlchemyRepository
from src.repositories import (
    permission as perm_,
    role as role_
)


class RolePermissionRepository(SQLAlchemyRepository):

    async def add_permissions_to_role(
        self,
        role_name: str,
        permissions: list[str]
    ) -> None:
        async with self._session() as session:
            role: Role = await role_.repository.get_by_filters(name=role_name)
            if not role:
                raise ObjectNotFound()

            for perm_name in permissions:
                permission: Permission = await perm_.repository.get_by_filters(
                    name=perm_name
                )
                if not permission:
                    raise ObjectNotFound()

                data: dict = {
                    'role_id': role.id,
                    'permission_id': permission.id
                }
                session.add(self._model(**data))

            await session.commit()


repository = RolePermissionRepository(RolePermission, get_session)
