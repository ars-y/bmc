from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


TokenDeps: type[str] = Annotated[str, Depends(oauth2_scheme)]
