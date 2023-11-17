from src.db.sessions import get_session
from src.models import Organization
from src.repositories.bases import SQLAlchemyRepository


class OrganizationRepository(SQLAlchemyRepository):

    _model: Organization


repository = OrganizationRepository(Organization, get_session)
