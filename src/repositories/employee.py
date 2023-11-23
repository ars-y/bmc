from src.models import Employee
from src.repositories.bases import SQLAlchemyRepository


class EmployeeRepository(SQLAlchemyRepository):

    _model = Employee
