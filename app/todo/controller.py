from app.user.repository import UserRepository
from core.exceptions import AppException

from .repository import TodoRepository
from .serializer import (
    CreateTodoSerializer,
    TodoSerializer,
    UpdateTodoSerializer,
)


class TodoController:
    def __init__(
        self, todo_repository: TodoRepository, user_repository: UserRepository
    ):
        self.todo_repository = todo_repository
        self.user_repository = user_repository

    def view_all_todos(self, request):
        paginator, result = self.todo_repository.index(request)
        serializer = TodoSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create_todo(self, request):
        serializer = CreateTodoSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            data["user_id"] = request.user.id
            todo = self.todo_repository.create(data)
            return TodoSerializer(todo)
        raise AppException.ValidationException(error_message=serializer.errors)

    def get_todo(self, obj_id: str):
        return TodoSerializer(self.todo_repository.find_by_id(obj_id))

    def update_todo(self, request, obj_id: str):
        serializer = UpdateTodoSerializer(data=request.data)
        if serializer.is_valid():
            todo = self.todo_repository.update_by_id(
                obj_id=obj_id, obj_data=serializer.data
            )
            return TodoSerializer(todo)
        raise AppException.ValidationException(error_message=serializer.errors)

    def delete_todo(self, obj_id: str):
        self.todo_repository.delete_by_id(obj_id)
        return None
