from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr


class RefUserMixin:
    """
    Declared attrs:

        - `user_id`: Foreign Key to User id.
    """

    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
