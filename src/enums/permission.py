from enum import Enum


class PermissionEnum(str, Enum):

    CREATE = 'create'
    EDIT = 'edit'
    DELETE = 'delete'
    READ = 'read'
    SHARE = 'share'


MANAGER_PERMISSIONS: tuple[PermissionEnum] = (
    PermissionEnum.CREATE,
    PermissionEnum.EDIT,
    PermissionEnum.READ,
    PermissionEnum.DELETE,
)


CONTRIBUTOR_PERMISSIONS: tuple[PermissionEnum] = (
    PermissionEnum.CREATE,
    PermissionEnum.EDIT,
    PermissionEnum.READ,
)
