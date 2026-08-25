from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        username = payload.get("sub")
        if not isinstance(username, str):
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
