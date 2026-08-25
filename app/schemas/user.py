from datetime import datetime

from sqlmodel import SQLModel


class UserCreate(SQLModel):
    email: str
    username: str
    password: str


class UserPublic(SQLModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
