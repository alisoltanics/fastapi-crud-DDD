from sqlmodel import Session, select

from app.domain.user.entity import User
from app.domain.user.repository import UserRepository
from app.domain.user.value_objects import Email, Password, Username
from app.infrastructure.db.models import UserTable


class SQLUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_domain(self, table: UserTable) -> User:
        return User(
            id=table.id,
            email=Email(table.email),
            username=Username(table.username),
            password=Password(table.hashed_password),
            is_active=table.is_active,
            created_at=table.created_at,
        )

    def _to_table(self, user: User) -> UserTable:
        return UserTable(
            id=user.id,
            email=str(user.email),
            username=str(user.username),
            hashed_password=user.password.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    def add(self, user: User) -> User:
        table = self._to_table(user)
        self.session.add(table)
        self.session.commit()
        self.session.refresh(table)
        return self._to_domain(table)

    def get_by_id(self, user_id: int) -> User | None:
        table = self.session.get(UserTable, user_id)
        return self._to_domain(table) if table else None

    def get_by_username(self, username: str) -> User | None:
        statement = select(UserTable).where(UserTable.username == username)
        table = self.session.exec(statement).first()
        return self._to_domain(table) if table else None

    def get_by_email(self, email: str) -> User | None:
        statement = select(UserTable).where(UserTable.email == email)
        table = self.session.exec(statement).first()
        return self._to_domain(table) if table else None

    def update(self, user: User) -> User:
        table = self._to_table(user)
        self.session.add(table)
        self.session.commit()
        self.session.refresh(table)
        return self._to_domain(table)
