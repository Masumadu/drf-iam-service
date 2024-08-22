from dataclasses import dataclass
from typing import Any, Dict

from django.conf import settings
from keycloak import (
    KeycloakAdmin,
    KeycloakOpenID,
    KeycloakOpenIDConnection,
)
from keycloak.exceptions import KeycloakError

from core.exceptions import AppException
from core.interfaces import AuthenticationInterface


@dataclass
class KeycloakAuthService(AuthenticationInterface):
    """
    This class is an intermediary between this service and the IAM service i.e Keycloak.
    It makes authentication and authorization API calls to the IAM service on
    behalf of the application. Use this class when authenticating an entity.
    """

    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url=settings.KEYCLOAK_SERVER_URL,
            realm_name=settings.KEYCLOAK_REALM,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        )
        keycloak_connection = KeycloakOpenIDConnection(
            server_url=settings.KEYCLOAK_SERVER_URL,
            username=settings.KEYCLOAK_ADMIN_USERNAME,
            password=settings.KEYCLOAK_ADMIN_PASSWORD,
            realm_name=settings.KEYCLOAK_REALM,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        )
        self.keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

    def get_token(self, obj_data: Dict[str, str]) -> Dict[str, str]:
        """
        Login to Keycloak and return token.

        :param obj_data: A dictionary containing username and password.
        :type obj_data: dict[str, str]
        :return: A dictionary containing token and refresh token.
        :rtype: dict[str, str]
        :raises AssertionError: If request data is missing or not a dict.
        """
        try:
            token_data = self.keycloak_openid.token(
                username=obj_data.get("username"), password=obj_data.get("password")
            )
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
            }
        except KeycloakError as exc:
            raise AppException.InternalServerException(
                f"{self.exc_message(exc)}"
            ) from exc

    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh the access token using a refresh token.

        :param refresh_token: A string containing the refresh token.
        :type refresh_token: str
        :return: A dictionary containing the token and refresh token.
        :rtype: dict[str, str]
        :raises AssertionError: If the refresh token is missing.
        """
        try:
            introspection = self.keycloak_openid.introspect(refresh_token)
            if not introspection.get("active"):
                raise AppException.BadRequestException(
                    error_message="refresh token is not active"
                )
            token_data = self.keycloak_openid.refresh_token(refresh_token)
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
            }
        except KeycloakError as exc:
            raise AppException.InternalServerException(
                f"{self.exc_message(exc)}"
            ) from exc

    def create_user(self, obj_data: dict) -> str:
        """
        Create a user in Keycloak.

        :param obj_data: A dictionary containing user data.
        :type obj_data: dict
        :return: The ID of the created user.
        :rtype: str
        :raises AssertionError: If the request data is missing or not a dict.
        """
        try:
            data: Dict[str, Any] = {
                "email": obj_data.get("email"),
                "username": obj_data.get("username"),
                "credentials": [
                    {
                        "value": obj_data.get("password"),
                        "type": "password",
                        "temporary": False,
                    }
                ],
                "enabled": True,
                "emailVerified": False,
                "access": {
                    "manageGroupMembership": True,
                    "view": True,
                    "mapRoles": True,
                    "impersonate": True,
                    "manage": True,
                },
            }
            return self.keycloak_admin.create_user(data)
        except KeycloakError as exc:
            raise AppException.InternalServerException(
                f"{self.exc_message(exc)}"
            ) from exc

    def update_user(self, obj_data: dict) -> dict:
        pass

    def delete_user(self, user_id: str) -> bool:
        pass

    def change_password(self, obj_data: dict) -> bool:
        """
        Change the password for a user in Keycloak.

        :param obj_data: The data for password reset.
        :type obj_data: dict
        :return: True if the password is successfully changed.
        :rtype: bool
        """
        try:
            self.keycloak_admin.set_user_password(
                user_id=obj_data.get("iam_user_id"),
                password=obj_data.get("password"),
                temporary=False,
            )
            return True
        except KeycloakError as exc:
            raise AppException.InternalServerException(
                f"{self.exc_message(exc)}"
            ) from exc

    def exc_message(self, exc):
        return exc.error_message or exc.response_body
