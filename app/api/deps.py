from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.application.auth.service import AuthService
from app.application.todo.service import TodoService
from app.application.user.service import UserService
from app.core.config import settings
from app.domain.user.entity import User
from app.domain.user.repository import UserRepository
from app.infrastructure.db.session import get_session
from app.infrastructure.repositories.todo_repository import SQLTodoRepository
from app.infrastructure.repositories.user_repository import SQLUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
SessionDep = Annotated[Session, Depends(get_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return SQLUserRepository(session)


def get_todo_repository(session: SessionDep) -> SQLTodoRepository:
    return SQLTodoRepository(session)


def get_user_service(user_repository: Annotated[UserRepository, Depends(get_user_repository)]) -> UserService:
    return UserService(user_repository)


def get_todo_service(todo_repository: Annotated[SQLTodoRepository, Depends(get_todo_repository)]) -> TodoService:
    return TodoService(todo_repository)


def get_auth_service(user_service: Annotated[UserService, Depends(get_user_service)]) -> AuthService:
    return AuthService(user_service)


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

    user_repo = SQLUserRepository(session)
    user = user_repo.get_by_username(username)
    if user is None:
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
