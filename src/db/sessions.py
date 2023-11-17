from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.engine import engine


LocalSession = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = LocalSession()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as sql_exc:
        await session.rollback()
        raise sql_exc
    except HTTPException as http_exc:
        await session.rollback()
        raise http_exc
    finally:
        await session.close()
