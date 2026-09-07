from abc import ABC, abstractmethod

from app.domain.user.entity import User


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    def update(self, user: User) -> User:
        ...
