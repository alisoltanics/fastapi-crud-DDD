from fastapi import HTTPException, status

from app.application.todo.dto import CreateTodoDTO, TodoResponseDTO, UpdateTodoDTO
from app.domain.todo.entity import Todo
from app.domain.todo.repository import TodoRepository
from app.domain.todo.value_objects import TodoDescription, TodoTitle


class TodoService:
    def __init__(self, todo_repository: TodoRepository) -> None:
        self.todo_repository = todo_repository

    def create(self, data: CreateTodoDTO, owner_id: int) -> TodoResponseDTO:
        todo = Todo(
            title=TodoTitle(data.title),
            description=TodoDescription(data.description),
            owner_id=owner_id,
        )
        saved_todo = self.todo_repository.add(todo)
        return TodoResponseDTO.from_domain(saved_todo)

    def get_by_id(self, todo_id: int, owner_id: int) -> Todo:
        todo = self.todo_repository.get_by_id(todo_id)
        if todo is None or not todo.belongs_to(owner_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found",
            )
        return todo

    def list_by_owner(self, owner_id: int) -> list[TodoResponseDTO]:
        todos = self.todo_repository.list_by_owner(owner_id)
        return [TodoResponseDTO.from_domain(t) for t in todos]

    def update(self, todo_id: int, owner_id: int, data: UpdateTodoDTO) -> TodoResponseDTO:
        todo = self.get_by_id(todo_id, owner_id)

        if data.title is not None:
            todo.change_title(TodoTitle(data.title))
        if data.description is not None:
            todo.change_description(TodoDescription(data.description))
        if data.completed is not None:
            if data.completed:
                todo.complete()
            else:
                todo.uncomplete()

        updated = self.todo_repository.update(todo)
        return TodoResponseDTO.from_domain(updated)

    def delete(self, todo_id: int, owner_id: int) -> None:
        todo = self.get_by_id(todo_id, owner_id)
        self.todo_repository.delete(todo)
