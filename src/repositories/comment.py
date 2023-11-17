from src.db.sessions import get_session
from src.models import Comment
from src.repositories.bases import SQLAlchemyRepository


class CommentRepository(SQLAlchemyRepository):
    pass


repository = CommentRepository(Comment, get_session)
