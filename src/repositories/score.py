from src.db.sessions import get_session
from src.models import Score
from src.repositories.bases import SQLAlchemyRepository


class ScoreRepository(SQLAlchemyRepository):
    pass


repository = ScoreRepository(Score, get_session)
