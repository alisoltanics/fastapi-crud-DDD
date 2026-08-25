from datetime import datetime

from sqlmodel import SQLModel


class TodoCreate(SQLModel):
    title: str
    description: str | None = None


class TodoUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoPublic(SQLModel):
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    owner_id: int
