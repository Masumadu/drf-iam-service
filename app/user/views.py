import pinject
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.utils import api_responses

from .controller import UserController
from .repository import UserRepository
from .serializer import (
    AuthTokenSerializer,
    ChangeUserPasswordSerializer,
    CreateUserSerializer,
    LoginUserSerializer,
    PaginatedUserSerializer,
    RefreshTokenSerializer,
    UpdateUserSerializer,
    UserQuerySerializer,
    UserSerializer,
)

obj_graph = pinject.new_object_graph(
    modules=None,
    classes=[UserController, UserRepository],
)
user_controller: UserController = obj_graph.provide(UserController)
api_doc_tag = ["User"]


@extend_schema(
    responses=api_responses(status_codes=[200, 401], schema=PaginatedUserSerializer),
    tags=api_doc_tag,
    parameters=[UserQuerySerializer],
)
@api_view(http_method_names=["GET"])
@permission_classes([IsAuthenticated])
def view_all_users(request):
    return user_controller.view_all_users(request)


@extend_schema(
    request=CreateUserSerializer,
    responses=api_responses(status_codes=[201, 409, 422], schema=UserSerializer),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["POST"])
def create_user(request):
    serializer = user_controller.create_user(request.data)
    return Response(data=serializer.data, status=201)


@extend_schema(
    responses=api_responses(status_codes=[200, 401, 404], schema=UserSerializer),
    tags=api_doc_tag,
)
@api_view(http_method_names=["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    serializer = user_controller.get_user(request)
    return Response(data=serializer.data, status=200)


@extend_schema(
    request=UpdateUserSerializer,
    responses=api_responses(
        status_codes=[200, 401, 404, 409, 422], schema=UserSerializer
    ),
    tags=api_doc_tag,
)
@api_view(http_method_names=["PATCH"])
@permission_classes([IsAuthenticated])
def update_user(request):
    serializer = user_controller.update_user(request=request)
    return Response(data=serializer.data, status=200)


@extend_schema(
    responses=api_responses(status_codes=[204, 401, 404], schema=None), tags=api_doc_tag
)
@api_view(http_method_names=["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request):
    result = user_controller.delete_user(request)
    return Response(data=result, status=204)


@extend_schema(
    request=LoginUserSerializer,
    responses=api_responses(status_codes=[200, 400, 422], schema=AuthTokenSerializer),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["POST"])
def login_user(request):
    result = user_controller.login_user(request)
    return Response(data=result, status=200)


@extend_schema(
    request=RefreshTokenSerializer,
    responses=api_responses(status_codes=[200, 400, 422], schema=AuthTokenSerializer),
    tags=api_doc_tag,
    auth=[],
)
@api_view(http_method_names=["POST"])
def refresh_user_token(request):
    result = user_controller.refresh_user_token(request)
    return Response(data=result, status=200)


@extend_schema(
    request=ChangeUserPasswordSerializer,
    responses=api_responses(
        status_codes=[204, 400, 401, 422], schema=AuthTokenSerializer
    ),
    tags=api_doc_tag,
)
@api_view(http_method_names=["POST"])
@permission_classes([IsAuthenticated])
def change_user_password(request):
    result = user_controller.change_user_password(request)
    return Response(data=result, status=200)
