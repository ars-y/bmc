from src.db.sessions import get_session
from src.models import Department
from src.repositories.bases import SQLAlchemyRepository


class DepartmentRepository(SQLAlchemyRepository):

    _model: Department


repository = DepartmentRepository(Department, get_session)
