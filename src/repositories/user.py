from src.db.sessions import get_session
from src.models import User
from src.repositories.bases import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    pass


repository = UserRepository(User, get_session)
