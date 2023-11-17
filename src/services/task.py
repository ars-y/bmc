from src.repositories import task
from src.services.bases import StorageBaseService


class TaskService(StorageBaseService):
    pass


service = TaskService(task.repository)
