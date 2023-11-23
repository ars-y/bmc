from src.models import Organization
from src.repositories.bases import SQLAlchemyRepository


class OrganizationRepository(SQLAlchemyRepository):

    _model = Organization
