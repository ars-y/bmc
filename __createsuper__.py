import asyncio

from src.core.constants import (
    SUPERUSER_PASSWORD,
    SUPERUSER_USERNAME
)
from src.core.settings.base import settings
from src import Role, User
from src.services import (
    permission as perm_db,
    role as role_db,
    role_permission as role_perm_db,
    user as user_db
)
from src.utils.security import pwd_guard


async def create_roles() -> None:
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
        await role_db.service.create(role_data)


async def create_permissions() -> None:
    name_filed: str = 'name'
    permissions: list = [
        {name_filed: 'create'},
        {name_filed: 'edit'},
        {name_filed: 'delete'},
        {name_filed: 'read'},
        {name_filed: 'share'},
    ]
    for perm_data in permissions:
        await perm_db.service.create(perm_data)


async def bound_roles_with_permissions() -> None:
    roles: tuple[str] = ('admin', 'owner', 'contributor', 'viewer')
    permissions: tuple[list[str]] = (
        ['create', 'edit', 'delete', 'read', 'share'],
        ['create', 'edit', 'delete', 'read', 'share'],
        ['create', 'edit', 'read'],
        ['read'],
    )
    for role_name, permission_names in zip(roles, permissions):
        await role_perm_db.service.add_permissions_to_role(
            role_name,
            permission_names
        )


async def create_superuser() -> None:
    role_name: str = 'admin'
    role: Role = await role_db.service.get_by_filters(name=role_name)
    if not role:
        role = await role_db.service.create({'name': role_name})

    data: dict = {
        'email': settings.SMTP_USER,
        'username': SUPERUSER_USERNAME,
        'hashed_password': pwd_guard.get_password_hash(SUPERUSER_PASSWORD),
        'is_active': True,
        'is_superuser': True,
        'role_id': role.id
    }

    user: User = await user_db.service.create(data)
    print('-'*80)
    print('Superuser is created with data:')
    print(user.to_pydantic_schema())
    print('-'*80)


async def main() -> None:
    await create_roles()
    await create_permissions()
    await bound_roles_with_permissions()
    await create_superuser()


if __name__ == '__main__':
    asyncio.run(main())
