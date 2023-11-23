from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.api.v1.schemas.response.comment import CommentResponseSchema
from src.models.bases import Base
from src.models.mixins.task import RefTaskMixin


class Comment(RefTaskMixin, Base):

    __tablename__ = 'comment'

    created_by: Mapped[int] = mapped_column(ForeignKey('employee.id'))
    content: Mapped[str]

    def to_pydantic_schema(self) -> CommentResponseSchema:
        return CommentResponseSchema(
            id=self.id,
            created_by=self.created_by,
            content=self.content,
            task_id=self.task_id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
