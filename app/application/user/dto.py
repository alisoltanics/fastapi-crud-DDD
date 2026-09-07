from datetime import datetime

from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    email: str
    username: str
    password: str


class UserResponseDTO(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, user) -> "UserResponseDTO":
        return cls(
            id=user.id,
            email=str(user.email),
            username=str(user.username),
            is_active=user.is_active,
            created_at=user.created_at,
        )
