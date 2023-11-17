from src.exceptions.bases import (
    BadRequest,
    NotAuthenticated,
    PermissionDenied
)


class InvalidToken(NotAuthenticated):

    DETAIL = 'Invalid token'


class AuthorizationError(PermissionDenied):

    DETAIL = 'Authorization failed. Access denied'


class InvationCodeError(BadRequest):

    DETAIL = 'Unknown invitation code'
