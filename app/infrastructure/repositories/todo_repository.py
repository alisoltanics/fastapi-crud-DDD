from sqlmodel import Session, select

from app.domain.todo.entity import Todo
from app.domain.todo.repository import TodoRepository
from app.domain.todo.value_objects import TodoDescription, TodoTitle
from app.infrastructure.db.models import TodoTable


class SQLTodoRepository(TodoRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_domain(self, table: TodoTable) -> Todo:
        return Todo(
            id=table.id,
            title=TodoTitle(table.title),
            description=TodoDescription(table.description) if table.description else None,
            completed=table.completed,
            created_at=table.created_at,
            owner_id=table.owner_id,
        )

    def _to_table(self, todo: Todo) -> TodoTable:
        return TodoTable(
            id=todo.id,
            title=str(todo.title),
            description=str(todo.description) if todo.description else None,
            completed=todo.completed,
            created_at=todo.created_at,
            owner_id=todo.owner_id,
        )

    def add(self, todo: Todo) -> Todo:
        table = self._to_table(todo)
        self.session.add(table)
        self.session.commit()
        self.session.refresh(table)
        return self._to_domain(table)

    def get_by_id(self, todo_id: int) -> Todo | None:
        table = self.session.get(TodoTable, todo_id)
        return self._to_domain(table) if table else None

    def list_by_owner(self, owner_id: int) -> list[Todo]:
        statement = select(TodoTable).where(TodoTable.owner_id == owner_id).order_by(TodoTable.id.desc())
        tables = self.session.exec(statement).all()
        return [self._to_domain(t) for t in tables]

    def update(self, todo: Todo) -> Todo:
        table = self._to_table(todo)
        self.session.add(table)
        self.session.commit()
        self.session.refresh(table)
        return self._to_domain(table)

    def delete(self, todo: Todo) -> None:
        table = self._to_table(todo)
        self.session.delete(table)
        self.session.commit()
