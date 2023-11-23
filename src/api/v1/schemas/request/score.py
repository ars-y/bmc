from pydantic import BaseModel, Field


class ScoreCreateSchema(BaseModel):

    integrity: int = Field(default=1, qe=1, le=10)
    quality: int = Field(default=1, qe=1, le=10)
