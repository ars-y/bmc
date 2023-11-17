from contextlib import asynccontextmanager
from typing import Generator

from fastapi import FastAPI

from src.cache.redis import RedisClient
from src.core.constants import TITLE_APP, DESCRIPTION_APP
from src.routers import app_routers


@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator:
    """Lifespan for redis client."""
    app.state.redis = await RedisClient.init_redis()
    yield
    await app.state.redis.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=TITLE_APP,
        description=DESCRIPTION_APP,
        lifespan=lifespan
    )

    for router in app_routers:
        app.include_router(router)

    return app


app = create_app()
