from fastapi import APIRouter, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.todo import TodoCreate, TodoPublic, TodoUpdate
from app.services.todos import (
    create_todo,
    delete_todo,
    get_todo,
    list_todos,
    update_todo,
)

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoPublic, status_code=status.HTTP_201_CREATED)
def create(data: TodoCreate, current_user: CurrentUser, session: SessionDep):
    return create_todo(session=session, data=data, owner_id=current_user.id)


@router.get("", response_model=list[TodoPublic])
def list_all(current_user: CurrentUser, session: SessionDep):
    return list_todos(session=session, owner_id=current_user.id)


@router.get("/{todo_id}", response_model=TodoPublic)
def get_one(todo_id: int, current_user: CurrentUser, session: SessionDep):
    return get_todo(session=session, todo_id=todo_id, owner_id=current_user.id)


@router.patch("/{todo_id}", response_model=TodoPublic)
def update(todo_id: int, data: TodoUpdate, current_user: CurrentUser, session: SessionDep):
    todo = get_todo(session=session, todo_id=todo_id, owner_id=current_user.id)
    return update_todo(session=session, todo=todo, data=data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(todo_id: int, current_user: CurrentUser, session: SessionDep):
    todo = get_todo(session=session, todo_id=todo_id, owner_id=current_user.id)
    delete_todo(session=session, todo=todo)
    return None
