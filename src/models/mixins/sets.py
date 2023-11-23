from src.models.mixins.departments import RefDepartmentMixin
from src.models.mixins.organizations import RefOrganizationMixin
from src.models.mixins.roles import RefRoleMixin
from src.models.mixins.users import RefUserMixin


class GenericUDORMixin(
    RefUserMixin,
    RefDepartmentMixin,
    RefOrganizationMixin,
    RefRoleMixin
):
    """Reference to User, Department, Organization and Role model."""
    pass
