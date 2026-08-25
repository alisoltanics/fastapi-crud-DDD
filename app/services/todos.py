from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


def create_todo(session: Session, data: TodoCreate, owner_id: int) -> Todo:
    todo = Todo(title=data.title, description=data.description, owner_id=owner_id)

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def get_todo(session: Session, todo_id: int, owner_id: int) -> Todo:
    todo = session.get(Todo, todo_id)

    if todo is None or todo.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return todo


def list_todos(session: Session, owner_id: int) -> list[Todo]:
    statement = select(Todo).where(Todo.owner_id == owner_id).order_by(Todo.id.desc())
    return list(session.exec(statement).all())


def update_todo(session: Session, todo: Todo, data: TodoUpdate) -> Todo:
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


def delete_todo(session: Session, todo: Todo) -> None:
    session.delete(todo)
    session.commit()
