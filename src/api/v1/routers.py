from fastapi import APIRouter

from src.api.v1.routes import auth, organizations, task, users


api_v1_router = APIRouter(prefix='/api/v1')

v1_routers: list = [
    auth.router,
    organizations.router,
    task.router,
    users.router
]

for router in v1_routers:
    api_v1_router.include_router(router)
