from src.db.sessions import get_session
from src.models import Permission
from src.repositories.bases import SQLAlchemyRepository


class PermissionRepository(SQLAlchemyRepository):
    pass


repository = PermissionRepository(Permission, get_session)
