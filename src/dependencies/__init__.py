from src.dependencies.auth import get_current_user
from src.dependencies.comment import get_comment_create_data
from src.dependencies.common import query_params_get_list
from src.dependencies.departments import (
    get_department_for_admin,
    get_department_for_employee
)
from src.dependencies.employee import (
    get_department_employee,
    get_organization_employee
)
from src.dependencies.meeting import (
    get_meeting_create_data,
    get_meeting_delete_data,
    get_meeting_update_data
)
from src.dependencies.organizations import get_current_organization
from src.dependencies.permissions import (
    get_current_admin,
    get_department_manager,
    get_department_contributor
)
from src.dependencies.score import get_task_score_create_data
from src.dependencies.task import (
    get_current_task,
    get_current_task_with_update_data,
    get_task_create_data,
    get_task_to_delete
)


__all__ = [
    'get_comment_create_data',
    'get_current_admin',
    'get_current_organization',
    'get_current_user',
    'get_current_task',
    'get_current_task_with_update_data',
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
    'get_task_to_delete',
    'query_params_get_list',
]
