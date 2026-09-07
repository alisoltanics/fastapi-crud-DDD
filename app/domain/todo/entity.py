from datetime import datetime, timezone

from app.domain.todo.value_objects import TodoDescription, TodoTitle


class Todo:
    def __init__(
        self,
        title: TodoTitle,
        owner_id: int,
        description: TodoDescription | None = None,
        completed: bool = False,
        id: int | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = created_at or datetime.now(timezone.utc)
        self.owner_id = owner_id

    def complete(self) -> None:
        self.completed = True

    def uncomplete(self) -> None:
        self.completed = False

    def change_title(self, new_title: TodoTitle) -> None:
        self.title = new_title

    def change_description(self, new_description: TodoDescription | None) -> None:
        self.description = new_description

    def belongs_to(self, user_id: int) -> bool:
        return self.owner_id == user_id
