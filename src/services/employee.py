from src.repositories import employee
from src.services.bases import StorageBaseService


class EmployeeService(StorageBaseService):
    pass


service = EmployeeService(employee.repository)
