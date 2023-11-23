from src.models import Role
from src.repositories.bases import SQLAlchemyRepository


class RoleRepository(SQLAlchemyRepository):

    _model = Role
