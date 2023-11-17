from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.enums.sql import OrderEnum
from src.exceptions.db import ObjectAlreadyExists, ObjectNotFound
from src.models.bases import Base


SQLModelType = TypeVar('SQLModelType', bound=Base)


class AbstractBaseRepository(ABC):

    _model = None

    @abstractmethod
    async def get(self, pk: int):
        """Returns an object from the database by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_filters(self, **filters):
        """Returns an object from the database by filters."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_field_contains(self, field: str, values: list):
        """
        Returns a list of objects from the database
        by fieled contains values.

        Args:
            - `field`: model attribute;
            - `values`: list of values to select.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self,
        filters: Optional[None] = None,
        offset: int = 0,
        limit: int = 100,
        order_by_field: Optional[str] = None,
        order: OrderEnum = OrderEnum.ASCENDING
    ):
        """
        Returns a list of objects from the database.

        Args:
            Optional:
            - `filters`: dict of the form
            {field_name: field_value} to filter by;
            - `offset`: number of skip rows;
            - `limit`: number of rows;
            - `order_by_field`: order by field;
            - `order`: ascending or descending.
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: dict):
        """Creates a new object in the database."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, pk: int, data: dict):
        """
        Updates an object in the database by ID.

        Args:
            - `pk`: object ID;
            - `data`: dict with data to update.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, pk: int):
        """Delete an object from the database by ID."""
        raise NotImplementedError


class SQLAlchemyRepository(AbstractBaseRepository):

    def __init__(
        self,
        model: type[SQLModelType],
        session: Callable[..., AsyncSession]
    ) -> None:
        self._model = model
        self._session = session

    async def get(self, pk: int) -> Optional[SQLModelType]:
        async with self._session() as session:
            stmt = select(self._model).where(self._model.id == pk)
            response = await session.execute(stmt)
            return response.scalar_one_or_none()

    async def get_by_filters(self, **filters) -> Optional[SQLModelType]:
        async with self._session() as session:
            stmt = select(self._model).filter_by(**filters)
            response = await session.execute(stmt)
            return response.scalar_one_or_none()

    async def get_by_field_contains(
        self,
        field: str,
        values: list
    ) -> list[SQLModelType]:
        async with self._session() as session:
            stmt = select(self._model)
            stmt = stmt.where(getattr(self._model, field).in_(values))
            response = await session.execute(stmt)
            return response.scalars().all()

    async def get_all(
        self,
        filters: Optional[dict] = None,
        offset: int = 0,
        limit: int = 10,
        order_by_field: Optional[str] = None,
        order: OrderEnum = OrderEnum.ASCENDING
    ) -> list[SQLModelType]:
        async with self._session() as session:
            stmt = select(self._model)
            if filters:
                stmt = stmt.filter_by(**filters)

            stmt = stmt.offset(offset).limit(limit)

            columns = self._model.__table__.columns
            if not order_by_field or order_by_field not in columns:
                order_by_field = self._model.id
            else:
                order_by_field = getattr(self._model, order_by_field)

            if order == OrderEnum.ASCENDING:
                stmt = stmt.order_by(order_by_field.asc())
            else:
                stmt = stmt.order_by(order_by_field.desc())

            response = await session.execute(stmt)
            return response.scalars().all()

    async def create(self, data: dict) -> SQLModelType:
        async with self._session() as session:
            db_obj = self._model(**data)
            try:
                session.add(db_obj)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise ObjectAlreadyExists()

            await session.refresh(db_obj)
            return db_obj

    async def update(self, pk: int, data: dict) -> SQLModelType:
        async with self._session() as session:
            obj: Optional[SQLModelType] = await self.get(pk)

            if not obj:
                raise ObjectNotFound()

            for field in data:
                setattr(obj, field, data.get(field))

            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def delete(self, pk: int) -> SQLModelType:
        async with self._session() as session:
            obj: Optional[SQLModelType] = await self.get(pk)

            if not obj:
                raise ObjectNotFound()

            await session.delete(obj)
            await session.commit()
            return obj
