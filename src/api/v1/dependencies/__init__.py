from src.api.v1.dependencies.auth import get_current_user
from src.api.v1.dependencies.comment import get_comment_create_data
from src.api.v1.dependencies.departments import (
    get_department_for_admin,
    get_department_for_employee
)
from src.api.v1.dependencies.employee import (
    get_department_employee,
    get_organization_employee
)
from src.api.v1.dependencies.meeting import (
    get_meeting_create_data,
    get_meeting_delete_data,
    get_meeting_update_data
)
from src.api.v1.dependencies.organizations import get_current_organization
from src.api.v1.dependencies.permissions import (
    get_current_admin,
    get_department_manager,
    get_department_contributor
)
from src.api.v1.dependencies.score import get_task_score_create_data
from src.api.v1.dependencies.task import (
    get_current_task,
    get_task_create_data,
    get_task_to_update,
    get_task_to_delete
)


__all__ = [
    'get_comment_create_data',
    'get_current_admin',
    'get_current_organization',
    'get_current_user',
    'get_current_task',
    'get_department_contributor',
    'get_department_employee',
    'get_department_for_admin',
    'get_department_for_employee',
    'get_department_manager',
    'get_meeting_create_data',
    'get_meeting_delete_data',
    'get_meeting_update_data',
    'get_organization_employee',
    'get_task_create_data',
    'get_task_score_create_data',
    'get_task_to_update',
    'get_task_to_delete',
]
