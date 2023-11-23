from pydantic import BaseModel


class CommentCreateSchema(BaseModel):

    content: str
