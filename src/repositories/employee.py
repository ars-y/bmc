from src.db.sessions import get_session
from src.models import Employee
from src.repositories.bases import SQLAlchemyRepository


class EmployeeRepository(SQLAlchemyRepository):

    _model: Employee


repository = EmployeeRepository(Employee, get_session)
