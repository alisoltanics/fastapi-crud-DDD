from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str | None = None
    completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    owner_id: int = Field(foreign_key="users.id", index=True)
