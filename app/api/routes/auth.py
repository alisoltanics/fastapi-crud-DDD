from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AuthServiceDep, SessionDep
from app.application.auth.dto import LoginDTO
from app.application.user.dto import CreateUserDTO, UserResponseDTO
from app.infrastructure.repositories.user_repository import SQLUserRepository
from app.application.user.service import UserService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=201,
)
def register(data: CreateUserDTO, auth_service: AuthServiceDep):
    return auth_service.register(data)


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
):
    return auth_service.login_with_credentials(
        username=form_data.username,
        password=form_data.password,
    )


@router.post("/login/json")
def login_json(data: LoginDTO, auth_service: AuthServiceDep):
    return auth_service.login(data)
