from src.repositories import department
from src.services.bases import StorageBaseService


class DepartmentService(StorageBaseService):
    pass


service = DepartmentService(department.repository)
