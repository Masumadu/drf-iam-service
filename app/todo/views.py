import pinject
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.user.repository import UserRepository
from core.utils import api_responses

from .controller import TodoController
from .repository import TodoRepository
from .serializer import (
    CreateTodoSerializer,
    PaginatedTodoSerializer,
    TodoQuerySerializer,
    TodoSerializer,
    UpdateTodoSerializer,
)

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[TodoController, TodoRepository, UserRepository],
)
todo_controller: TodoController = obj_graph.provide(TodoController)
api_doc_tag = ["Todo"]


@extend_schema(
    responses=api_responses(status_codes=[200, 401], schema=PaginatedTodoSerializer),
    tags=api_doc_tag,
    parameters=[TodoQuerySerializer],
)
@api_view(http_method_names=["GET"])
@permission_classes([IsAuthenticated])
def view_all_todos(request):
    return todo_controller.view_all_todos(request)


@extend_schema(
    request=CreateTodoSerializer,
    responses=api_responses(status_codes=[201, 401, 409, 422], schema=TodoSerializer),
    tags=api_doc_tag,
)
@api_view(http_method_names=["POST"])
@permission_classes([IsAuthenticated])
def create_todo(request):
    serializer = todo_controller.create_todo(request)
    return Response(data=serializer.data, status=201)


@extend_schema(
    responses=api_responses(status_codes=[200, 401, 404], schema=TodoSerializer),
    tags=api_doc_tag,
)
@api_view(http_method_names=["GET"])
@permission_classes([IsAuthenticated])
def get_todo(request, todo_id):
    serializer = todo_controller.get_todo(todo_id)
    return Response(data=serializer.data, status=200)


@extend_schema(
    request=UpdateTodoSerializer,
    responses=api_responses(
        status_codes=[200, 401, 404, 409, 422], schema=TodoSerializer
    ),
    tags=api_doc_tag,
)
@api_view(http_method_names=["PATCH"])
@permission_classes([IsAuthenticated])
def update_todo(request, todo_id):
    serializer = todo_controller.update_todo(request=request, obj_id=todo_id)
    return Response(data=serializer.data, status=200)


@extend_schema(
    responses=api_responses(status_codes=[204, 401, 404], schema=None), tags=api_doc_tag
)
@api_view(http_method_names=["DELETE"])
@permission_classes([IsAuthenticated])
def delete_todo(request, todo_id):
    result = todo_controller.delete_todo(todo_id)
    return Response(data=result, status=204)
