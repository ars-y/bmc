from src.models import Permission
from src.repositories.bases import SQLAlchemyRepository


class PermissionRepository(SQLAlchemyRepository):

    _model = Permission
