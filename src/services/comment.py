from src.repositories import comment
from src.services.bases import StorageBaseService


class CommentService(StorageBaseService):
    pass


service = CommentService(comment.repository)
