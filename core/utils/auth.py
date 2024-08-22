from typing import Optional, Tuple

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from jwt import PyJWTError
from rest_framework import permissions
from rest_framework.authentication import BaseAuthentication

from app.account.models import AccountModel
from core.constants import GroupEnum
from core.exceptions import AppException
from core.services import KeycloakAuthService


class KeycloakAuthentication(BaseAuthentication, KeycloakAuthService):
    def authenticate(self, request):
        scheme, token = self.get_authorization_scheme(
            request.headers.get("Authorization")
        )
        if not (scheme and token):
            raise AppException.UnauthorizedException(error_message="unauthenticated")
        if scheme != "Bearer":
            raise AppException.UnauthorizedException(
                error_message="invalid authentication scheme"
            )
        try:
            iam_data = self.keycloak_openid.decode_token(token)
            account = AccountModel.objects.get(pk=iam_data.get("preferred_username"))
            return account, None
        except PyJWTError as exc:
            raise AppException.BadRequestException(error_message=exc.args) from exc

    def get_authorization_scheme(
        self, authorization_value: Optional[str]
    ) -> Tuple[str, str]:
        if not authorization_value:
            return "", ""
        scheme, _, param = authorization_value.partition(" ")
        return scheme, param


class KeycloakAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "core.utils.auth.KeycloakAuthentication"
    name = "KeycloakAuthenticationScheme"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
        }


class IsSuperAdmin(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return GroupEnum.super_admin.value in [
                group.name for group in request.user.groups.all()
            ]
        return False
