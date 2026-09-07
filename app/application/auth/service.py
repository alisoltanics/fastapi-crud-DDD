from fastapi import HTTPException, status

from app.application.auth.dto import LoginDTO, TokenDTO
from app.application.user.dto import CreateUserDTO, UserResponseDTO
from app.application.user.service import UserService
from app.core.security import create_access_token, verify_password


class AuthService:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    def register(self, data: CreateUserDTO) -> UserResponseDTO:
        return self.user_service.register(data)

    def login(self, data: LoginDTO) -> TokenDTO:
        user = self.user_service.get_by_username(data.username)

        if not user or not verify_password(data.password, user.password.value):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(subject=str(user.username))
        return TokenDTO(access_token=access_token, token_type="bearer")

    def login_with_credentials(self, username: str, password: str) -> TokenDTO:
        user = self.user_service.get_by_username(username)

        if not user or not verify_password(password, user.password.value):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(subject=str(user.username))
        return TokenDTO(access_token=access_token, token_type="bearer")
