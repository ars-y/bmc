from src.db.sessions import get_session
from src.models import Role
from src.repositories.bases import SQLAlchemyRepository


class RoleRepository(SQLAlchemyRepository):
    pass


repository = RoleRepository(Role, get_session)
