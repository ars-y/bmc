from typing import Any, Optional, Union

import jwt


def generate(
    payload: dict[str, Any],
    key: Union[str, bytes],
    algorithm: Optional[str] = None
) -> str:
    """Returns generated JSON Web Token."""
    return jwt.encode(payload, key, algorithm)


def decode(
    token: Union[str, bytes],
    key: Optional[Union[str, bytes]] = None,
    algorithms: Optional[list] = None
) -> dict[str, Any]:
    """Decodes token and return payload data."""
    return jwt.decode(token, key, algorithms)
