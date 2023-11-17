from src.repositories import permission
from src.services.bases import StorageBaseService


class PermissionService(StorageBaseService):
    pass


service = PermissionService(permission.repository)
