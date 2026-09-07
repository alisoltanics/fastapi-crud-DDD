from fastapi import HTTPException, status

from app.application.user.dto import CreateUserDTO, UserResponseDTO
from app.core.security import hash_password
from app.domain.user.entity import User
from app.domain.user.repository import UserRepository
from app.domain.user.value_objects import Email, Password, Username


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register(self, data: CreateUserDTO) -> UserResponseDTO:
        if self.user_repository.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        if self.user_repository.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
            email=Email(data.email),
            username=Username(data.username),
            password=Password(data.password),
        )

        hashed = hash_password(data.password)
        user.password = Password(hashed)

        saved_user = self.user_repository.add(user)
        return UserResponseDTO.from_domain(saved_user)

    def get_by_username(self, username: str) -> User | None:
        return self.user_repository.get_by_username(username)

    def get_current_user(self, user: User) -> UserResponseDTO:
        return UserResponseDTO.from_domain(user)
