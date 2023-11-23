from src.models import Score
from src.repositories.bases import SQLAlchemyRepository


class ScoreRepository(SQLAlchemyRepository):

    _model = Score
