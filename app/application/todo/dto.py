from datetime import datetime

from pydantic import BaseModel


class CreateTodoDTO(BaseModel):
    title: str
    description: str | None = None


class UpdateTodoDTO(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoResponseDTO(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    owner_id: int

    @classmethod
    def from_domain(cls, todo) -> "TodoResponseDTO":
        return cls(
            id=todo.id,
            title=str(todo.title),
            description=str(todo.description) if todo.description else None,
            completed=todo.completed,
            created_at=todo.created_at,
            owner_id=todo.owner_id,
        )
