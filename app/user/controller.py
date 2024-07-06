from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import AppException

from .repository import UserRepository
from .serializer import (
    ChangeUserPasswordSerializer,
    CreateUserSerializer,
    LoginUserSerializer,
    RefreshTokenSerializer,
    UpdateUserSerializer,
    UserSerializer,
)


class UserController:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def view_all_users(self, request):
        paginator, result = self.user_repository.index(request)
        serializer = UserSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create_user(self, obj_data: dict):
        serializer = CreateUserSerializer(data=obj_data)
        if serializer.is_valid():
            user = self.user_repository.create(serializer.data)
            return UserSerializer(user)
        raise AppException.ValidationException(error_message=serializer.errors)

    def get_user(self, request):
        return UserSerializer(self.user_repository.find_by_id(request.user.id))

    def update_user(self, request):
        serializer = UpdateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = self.user_repository.update_by_id(
                obj_id=request.user.id, obj_data=serializer.data
            )
            return UserSerializer(user)
        raise AppException.ValidationException(error_message=serializer.errors)

    def delete_user(self, request):
        self.user_repository.delete_by_id(request.user.id)
        return None

    # noinspection PyMethodMayBeStatic
    def get_token(self, user):
        try:
            token = RefreshToken.for_user(user)
            return {
                "access_token": str(token.access_token),  # noqa
                "refresh_token": str(token),
            }
        except TokenError:
            raise AppException.BadRequestException(error_message="invalid credentials")

    # noinspection PyMethodMayBeStatic
    def refresh_token(self, refresh_token):
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return {
                "access_token": str(token.access_token),
                "refresh_token": str(token),
            }
        except TokenError:
            raise AppException.BadRequestException(
                error_message="refresh token invalid"
            )

    def login_user(self, request):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request=request,
                username=serializer.data.get("username"),
                password=serializer.data.get("password"),
            )
            if user:
                return self.get_token(user)
            raise AppException.BadRequestException(
                error_message="username or password invalid"
            )
        raise AppException.ValidationException(error_message=serializer.errors)

    def refresh_user_token(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            return self.refresh_token(
                refresh_token=serializer.data.get("refresh_token")
            )
        raise AppException.ValidationException(error_message=serializer.errors)

    def change_user_password(self, request):
        serializer = ChangeUserPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request=request,
                username=request.user.username,
                password=serializer.data.get("old_password"),
            )
            if user:
                request.user.set_password(serializer.data.get("new_password"))
                request.user.save()
                return self.get_token(user)
            raise AppException.BadRequestException(
                error_message="username or password invalid"
            )
        raise AppException.ValidationException(error_message=serializer.errors)
