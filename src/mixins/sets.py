from src.mixins.departments import RefDepartmentMixin
from src.mixins.organizations import RefOrganizationMixin
from src.mixins.roles import RefRoleMixin
from src.mixins.users import RefUserMixin


class GenericUDORMixin(
    RefUserMixin,
    RefDepartmentMixin,
    RefOrganizationMixin,
    RefRoleMixin
):
    """Reference to User, Department, Organization and Role model."""
    pass
