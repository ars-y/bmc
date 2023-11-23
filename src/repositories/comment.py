from src.models import Comment
from src.repositories.bases import SQLAlchemyRepository


class CommentRepository(SQLAlchemyRepository):

    _model = Comment
