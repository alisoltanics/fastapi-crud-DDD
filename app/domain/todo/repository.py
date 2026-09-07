from abc import ABC, abstractmethod

from app.domain.todo.entity import Todo


class TodoRepository(ABC):
    @abstractmethod
    def add(self, todo: Todo) -> Todo:
        ...

    @abstractmethod
    def get_by_id(self, todo_id: int) -> Todo | None:
        ...

    @abstractmethod
    def list_by_owner(self, owner_id: int) -> list[Todo]:
        ...

    @abstractmethod
    def update(self, todo: Todo) -> Todo:
        ...

    @abstractmethod
    def delete(self, todo: Todo) -> None:
        ...
