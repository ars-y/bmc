from src.exceptions.bases import NotFound, ConflictError


class ObjectNotFound(NotFound):

    DETAIL = 'Object not found'


class ObjectAlreadyExists(ConflictError):

    DETAIL = 'Object already exists'
