import secrets
import uuid

from core.services import KeycloakAuthService


class MockKeycloakAuthService(KeycloakAuthService):
    tokens = {
        "access_token": secrets.token_urlsafe(128),
        "refresh_token": secrets.token_urlsafe(128),
    }

    def get_token(self, *args, **kwargs):
        return self.tokens

    def refresh_token(self, *args, **kwargs):
        return self.tokens

    def create_user(self, *args, **kwargs):
        return str(uuid.uuid4())

    def change_password(self, *args, **kwargs):
        return True
