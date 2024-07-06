from rest_framework import serializers

from core.serializers import PaginatedSerializer


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    username = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.EmailField()


class PaginatedUserSerializer(PaginatedSerializer):
    results = UserSerializer(many=True)


class CreateUserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def to_representation(self, instance):
        # Use the default representation
        representation = super().to_representation(instance)
        # Rename the password field to secret
        if "password" in representation:
            representation["secret"] = representation.pop("password")
        return representation


class UpdateUserSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class AuthTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class ChangeUserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=50)
