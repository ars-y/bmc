from src.db.sessions import get_session
from src.models import Task
from src.repositories.bases import SQLAlchemyRepository


class TaskRepository(SQLAlchemyRepository):
    pass


repository = TaskRepository(Task, get_session)
