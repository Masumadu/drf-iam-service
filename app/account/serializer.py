from rest_framework import serializers

from core.constants import GroupEnum
from core.serializers import EnumFieldSerializer, PaginatedSerializer


class AccountSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    username = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    iam_provider_id = serializers.CharField(required=True)
    is_email_verified = serializers.BooleanField(required=True)
    is_phone_verified = serializers.BooleanField(required=True)
    api_key_enabled = serializers.BooleanField(required=True)
    status = serializers.CharField(required=True)
    last_login = serializers.DateTimeField(required=False)
    is_active = serializers.BooleanField(required=True)


class PaginatedAccountSerializer(PaginatedSerializer):
    results = AccountSerializer(many=True)


class CreateAccountSerializer(serializers.Serializer):
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


class UpdateAccountSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class LoginAccountSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class AuthTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class ChangeAccountPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class AccountApikeySerializer(serializers.Serializer):
    apikey = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=True)


class ResetAccountPasswordSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    new_password = serializers.CharField(required=True)
    sec_code = serializers.CharField(required=True)


class AccountQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1)
    page_size = serializers.IntegerField(default=50)


class ConfirmOtpSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    otp_code = serializers.CharField(required=True)


class ConfirmOtpResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    sec_code = serializers.CharField(required=True)


class GenerateApiKeySerializer(serializers.Serializer):
    apikey = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=True)


class UpdateAccountGroupSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    group = EnumFieldSerializer(enum=GroupEnum, enum_use_values=True, required=True)
