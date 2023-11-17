from src.repositories import score
from src.services.bases import StorageBaseService


class ScoreService(StorageBaseService):
    pass


service = ScoreService(score.repository)
