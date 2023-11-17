from sqlalchemy.ext.asyncio import create_async_engine

from src.core.settings.base import settings


engine = create_async_engine(str(settings.DATABASE_URL))
