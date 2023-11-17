from enum import Enum


class RoleEnum(str, Enum):

    ADMIN = 'admin'
    OWNER = 'owner'
    CONTRIBUTOR = 'contributor'
    VIEWER = 'viewer'
