from abc import ABC, abstractmethod, abstractclassmethod
from typing import TypeVar, Optional

from pydantic import BaseModel

from src.models.bases import Base
from src.units.base import AbstractBaseUnitOfWork


SQLModelType = TypeVar('SQLModelType', bound=Base)
PyModelType = TypeVar('PyModelType', bound=BaseModel)
UOWType = TypeVar('UOWType', bound=AbstractBaseUnitOfWork)


class AbstractBaseService(ABC):

    _repository = None

    @abstractclassmethod
    async def get(cls, uow: type[UOWType], pk: int):
        raise NotImplementedError

    @abstractclassmethod
    async def get_by_field_contains(
        cls,
        uow: type[UOWType],
        field: str,
        values: list
    ):
        raise NotImplementedError

    @abstractclassmethod
    async def get_all(cls, uow: type[UOWType], filters: dict):
        raise NotImplementedError

    @abstractclassmethod
    async def get_by_filters(cls, uow: type[UOWType], **filters):
        raise NotImplementedError

    @abstractclassmethod
    async def create(cls, uow: type[UOWType], data: dict):
        raise NotImplementedError

    @abstractclassmethod
    async def update(cls, uow: type[UOWType], pk: int, data: dict):
        raise NotImplementedError

    @abstractclassmethod
    async def delete(cls, uow: type[UOWType], pk: int):
        raise NotImplementedError


class StorageBaseService(AbstractBaseService):

    @classmethod
    async def get(cls, uow: type[UOWType], pk: int):
        """Returns an object from the database by ID.."""
        async with uow:
            return await uow.__dict__[cls._repository].get(pk)

    @classmethod
    async def get_by_field_contains(
        cls,
        uow: type[UOWType],
        field: str,
        values: list
    ) -> list[SQLModelType]:
        """
        Returns a list of objects from the database
        by fieled contains values.
        """
        async with uow:
            return await uow.__dict__[cls._repository].get_by_field_contains(
                field=field,
                values=values
            )

    @classmethod
    async def get_all(
        cls,
        uow: type[UOWType],
        filters: Optional[dict] = None
    ) -> list[SQLModelType]:
        """Returns a list of objects from the database.."""
        filters: dict = filters or {}
        async with uow:
            return await uow.__dict__[cls._repository].get_all(**filters)

    @classmethod
    async def get_by_filters(
        cls,
        uow: type[UOWType],
        **filters
    ) -> Optional[SQLModelType]:
        """Returns an object from the database by filters."""
        async with uow:
            return (
                await uow.__dict__[cls._repository]
                .get_by_filters(**filters)
            )

    @classmethod
    async def create(cls, uow: type[UOWType], data: dict) -> SQLModelType:
        """Creates a new object in the database."""
        async with uow:
            return await uow.__dict__[cls._repository].create(data)

    @classmethod
    async def update(
        cls,
        uow: type[UOWType],
        pk: int,
        data: dict
    ) -> SQLModelType:
        """Updates an object in the database by ID."""
        async with uow:
            return await uow.__dict__[cls._repository].update(pk, data)

    @classmethod
    async def delete(cls, uow: type[UOWType], pk: int) -> SQLModelType:
        """Delete an object from the database by ID.."""
        async with uow:
            return await uow.__dict__[cls._repository].delete(pk=pk)


class TokenAbstractBaseService(ABC):

    @abstractmethod
    async def write(self, model: type[SQLModelType]) -> dict:
        """Returns generated tokens."""
        raise NotImplementedError

    @abstractmethod
    async def read(self, token: str) -> dict:
        """Returns the token payload."""
        raise NotImplementedError

    @abstractmethod
    async def remove(self, token: str) -> None:
        """Delete token if it exists."""
        raise NotImplementedError
