from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr


class GenericFieldsMixin:
    """
    Declared attrs:
        - `name`: default unique -- True;
        - `description`: default nullable -- True.
    """

    _name_unique: bool = True
    _description_nullable: bool = True

    @declared_attr
    def name(cls) -> Mapped[str]:
        return mapped_column(String, unique=cls._name_unique)

    @declared_attr
    def description(cls) -> Mapped[str]:
        return mapped_column(String, nullable=cls._description_nullable)
