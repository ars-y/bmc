from src.models import Department
from src.repositories.bases import SQLAlchemyRepository


class DepartmentRepository(SQLAlchemyRepository):

    _model = Department
