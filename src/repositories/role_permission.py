from sqlalchemy import select

from src.exceptions.db import ObjectNotFound
from src.models import Permission, Role, RolePermission
from src.repositories.bases import SQLAlchemyRepository


class RolePermissionRepository(SQLAlchemyRepository):

    _model = RolePermission

    async def add_permissions_to_role(
        self,
        role_name: str,
        permissions: list[str]
    ) -> None:
        stmt = select(Role).filter_by(name=role_name)
        response = await self._session.execute(stmt)
        role: Role = response.scalar_one_or_none()

        if not role:
            raise ObjectNotFound()

        for perm_name in permissions:
            stmt = select(Permission).filter_by(name=perm_name)
            response = await self._session.execute(stmt)
            permission: Permission = response.scalar_one_or_none()
            if not permission:
                raise ObjectNotFound()

            data: dict = {
                'role_id': role.id,
                'permission_id': permission.id
            }
            self._session.add(self._model(**data))
