import re

from src.core.constants import PasswordConst, ErrorCode


PASSWORD_PATTERN = re.compile(PasswordConst.PATTERN)


def password_validator(password: str) -> str:
    if not re.match(PASSWORD_PATTERN, password):
        raise ValueError(ErrorCode.INCORRECT_PASSWORD)

    return password
