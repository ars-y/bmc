from typing import Annotated

from fastapi import Depends

from src.dependencies.permissions import get_current_admin
from src.exceptions.bases import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.models import Organization, User
from src.services import organization as org_db


async def get_current_organization(
    org_id: int,
    current_user: Annotated[User, Depends(get_current_admin)]
) -> dict:
    """
    Returns a dict with an organization db object
    and the current admin of that organization.
    """
    organization: Organization = await org_db.service.get(org_id)
    if not organization:
        error_info: dict = {
            'reason': 'Object not found',
            'description': 'The specified organization doesn\'t exists'
        }
        raise ObjectNotFound(extra_msg=error_info)

    if current_user.id != organization.user_id:
        error_info: dict = {
            'reason': 'Permission denied',
            'description': 'You need to be the creator of this organization'
        }
        raise PermissionDenied(extra_msg=error_info)

    return {
        'organization': organization,
        'current_user': current_user
    }
