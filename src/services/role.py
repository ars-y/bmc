from src.repositories import role
from src.services.bases import StorageBaseService


class RoleService(StorageBaseService):
    pass


service = RoleService(role.repository)
