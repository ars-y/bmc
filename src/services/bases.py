from abc import ABC, abstractmethod
from typing import TypeVar, Optional

from pydantic import BaseModel

from src.models.bases import Base
from src.repositories.bases import SQLAlchemyRepository


RepoType = TypeVar('RepoType', bound=SQLAlchemyRepository)
SQLModelType = TypeVar('SQLModelType', bound=Base)
PyModelType = TypeVar('PyModelType', bound=BaseModel)


class StorageBaseService:

    _repository: type[RepoType]

    def __init__(self, repository: type[RepoType]) -> None:
        self._repository = repository

    async def get(self, pk: int) -> Optional[SQLModelType]:
        """Returns an object from the database by ID.."""
        return await self._repository.get(pk=pk)

    async def get_by_field_contains(
        self,
        field: str,
        values: list
    ) -> list[SQLModelType]:
        """
        Returns a list of objects from the database
        by fieled contains values.
        """
        return await self._repository.get_by_field_contains(
            field=field,
            values=values
        )

    async def get_all(
        self,
        filters: Optional[dict] = None
    ) -> list[SQLModelType]:
        """Returns a list of objects from the database.."""
        filters: dict = filters or {}
        return await self._repository.get_all(**filters)

    async def get_by_filters(self, **filters) -> Optional[SQLModelType]:
        """Returns an object from the database by filters."""
        return await self._repository.get_by_filters(**filters)

    async def create(self, data: dict) -> SQLModelType:
        """Creates a new object in the database."""
        return await self._repository.create(data)

    async def update(self, pk: int, data: dict) -> SQLModelType:
        """Updates an object in the database by ID."""
        return await self._repository.update(pk, data)

    async def delete(self, pk: int) -> SQLModelType:
        """Delete an object from the database by ID.."""
        return await self._repository.delete(pk=pk)


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
