import asyncio

from src import Role, User
from src.core.constants import (
    SUPERUSER_PASSWORD,
    SUPERUSER_USERNAME
)
from src.core.settings.base import settings
from src.dependencies.unit_of_work import get_uow
from src.services import (
    PermissionService,
    RoleService,
    RolePermissionService,
    UserService
)
from src.utils.security import pwd_guard


async def create_roles(uow) -> None:
    roles: list[dict[str, str]] = [
        {
            'name': 'admin',
            'description': 'Organization level administrator'
        },
        {
            'name': 'owner',
            'description': 'Department owner level'
        },
        {
            'name': 'contributor',
            'description': 'Department member level'
        },
        {
            'name': 'viewer',
            'description': 'Department viewer level'
        },
    ]
    for role_data in roles:
        await RoleService.create(uow, role_data)


async def create_permissions(uow) -> None:
    name_filed: str = 'name'
    permissions: list = [
        {name_filed: 'create'},
        {name_filed: 'edit'},
        {name_filed: 'delete'},
        {name_filed: 'read'},
        {name_filed: 'share'},
    ]
    for perm_data in permissions:
        await PermissionService.create(uow, perm_data)


async def bound_roles_with_permissions(uow) -> None:
    roles: tuple[str] = ('admin', 'owner', 'contributor', 'viewer')
    permissions: tuple[list[str]] = (
        ['create', 'edit', 'delete', 'read', 'share'],
        ['create', 'edit', 'delete', 'read', 'share'],
        ['create', 'edit', 'read'],
        ['read'],
    )
    for role_name, permission_names in zip(roles, permissions):
        await RolePermissionService.add_permissions_to_role(
            uow,
            role_name,
            permission_names
        )


async def create_superuser(uow) -> None:
    role_name: str = 'admin'
    role: Role = await RoleService.get_by_filters(uow, name=role_name)
    if not role:
        role = await RoleService.create(uow, {'name': role_name})

    data: dict = {
        'email': settings.SMTP_USER,
        'username': SUPERUSER_USERNAME,
        'hashed_password': pwd_guard.get_password_hash(SUPERUSER_PASSWORD),
        'is_active': True,
        'is_superuser': True,
        'role_id': role.id
    }

    user: User = await UserService.create(uow, data)
    print('-'*80)
    print('Superuser is created with data:')
    print(user.to_pydantic_schema())
    print('-'*80)


async def main() -> None:
    uow = next(get_uow())
    await create_roles(uow)
    await create_permissions(uow)
    await bound_roles_with_permissions(uow)
    await create_superuser(uow)


if __name__ == '__main__':
    asyncio.run(main())
