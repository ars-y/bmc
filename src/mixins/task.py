from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr


class RefTaskMixin:
    """
    Declared attrs:

        - `task_id`: Foreign Key to Task id
        that can be unique (default -- False);
    """
    _task_is_unique: bool = False

    @declared_attr
    def task_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey('task.id'),
            unique=cls._task_is_unique
        )
