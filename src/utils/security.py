import secrets
from typing import Optional

from passlib.context import CryptContext


class PWDGuard:

    _context: CryptContext

    def __init__(self, schemes: list[str]) -> None:
        self._context = CryptContext(schemes, deprecated='auto')

    def verify_password(self, password: str, hashed_password: bytes) -> bool:
        """Verify password against an existing hash."""
        return self._context.verify(bytes(password, 'utf-8'), hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Returns hash for password."""
        return self._context.hash(bytes(password, 'utf-8'))


pwd_guard = PWDGuard(['bcrypt'])


def generate_url_token(length: Optional[int] = None) -> str:
    return secrets.token_urlsafe(length)
