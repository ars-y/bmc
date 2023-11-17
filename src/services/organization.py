from src.repositories import organization
from src.services.bases import StorageBaseService


class OgranizationService(StorageBaseService):
    pass


service = OgranizationService(organization.repository)
