from fastapi import APIRouter, status

from app.api.deps import CurrentUser, TodoServiceDep
from app.application.todo.dto import CreateTodoDTO, TodoResponseDTO, UpdateTodoDTO

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoResponseDTO, status_code=status.HTTP_201_CREATED)
def create(data: CreateTodoDTO, current_user: CurrentUser, todo_service: TodoServiceDep):
    return todo_service.create(data=data, owner_id=current_user.id)


@router.get("", response_model=list[TodoResponseDTO])
def list_all(current_user: CurrentUser, todo_service: TodoServiceDep):
    return todo_service.list_by_owner(owner_id=current_user.id)


@router.get("/{todo_id}", response_model=TodoResponseDTO)
def get_one(todo_id: int, current_user: CurrentUser, todo_service: TodoServiceDep):
    todo = todo_service.get_by_id(todo_id=todo_id, owner_id=current_user.id)
    return TodoResponseDTO.from_domain(todo)


@router.patch("/{todo_id}", response_model=TodoResponseDTO)
def update(todo_id: int, data: UpdateTodoDTO, current_user: CurrentUser, todo_service: TodoServiceDep):
    return todo_service.update(todo_id=todo_id, owner_id=current_user.id, data=data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(todo_id: int, current_user: CurrentUser, todo_service: TodoServiceDep):
    todo_service.delete(todo_id=todo_id, owner_id=current_user.id)
    return None
