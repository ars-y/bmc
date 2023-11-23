from src.exceptions.bases import PermissionDenied
from src.exceptions.db import ObjectNotFound
from src.models import Organization, User
from src.services import OrganizationService
from src.units.unit_of_work import UnitOfWork


async def get_current_organization(
    org_id: int,
    uow: UnitOfWork,
    current_user: User
) -> Organization:
    """Returns an organization database object."""
    organization: Organization = await OrganizationService.get(uow, org_id)
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

    return organization
