from src.routers.auth import router as auth_router
from src.routers.organizations import router as org_router
from src.routers.task import router as task_router
from src.routers.users import router as user_router


app_routers: list = [
    auth_router,
    org_router,
    task_router,
    user_router,
]
