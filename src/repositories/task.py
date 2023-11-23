from src.models import Task
from src.repositories.bases import SQLAlchemyRepository


class TaskRepository(SQLAlchemyRepository):

    _model = Task
