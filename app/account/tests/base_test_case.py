from unittest import mock

from django.conf import settings

from app.account.controller import AccountController
from app.account.models import AccountModel
from app.account.repository import AccountRepository
from tests import BaseTestCase, MockKeycloakAuthService, MockSideEffects

from .test_data import AccountTestData


class AccountTestCase(BaseTestCase, MockSideEffects):
    def setup_test_data(self):
        self.account_test_data = AccountTestData()
        self.account_model = AccountModel.objects.create(
            **self.account_test_data.existing_account
        )
        self.super_admin_model = AccountModel.objects.filter(
            username=settings.SUPER_ADMIN_USERNAME
        ).get()
        super().setup_test_data()
        self.token = {
            "refresh_token": self.refresh_token,
            "access_token": self.access_token,
        }

    def instantiate_classes(self):
        """This is where all classes are instantiated for the test"""
        self.account_repository = AccountRepository()
        self.mock_keycloak_auth = MockKeycloakAuthService()
        self.account_controller = AccountController(
            account_repository=self.account_repository,
            keycloak_auth_service=self.mock_keycloak_auth,
        )
        super().instantiate_classes()

    def setup_patches(self):
        """This is where all mocked object are setup for the test"""
        decode = mock.patch(
            "core.services.keycloak_service.KeycloakOpenID.decode_token"
        )
        self.addCleanup(decode.stop)
        self.jwt_decode = decode.start()
        self.random_choices_patcher = mock.patch(
            "app.account.controller.choices", self.random_number
        )
        self.addCleanup(self.random_choices_patcher.stop)
        self.random_choices_patcher.start()
        super().setup_patches()

    # noinspection PyMethodMayBeStatic
    def mock_decode_token(self, *args, **kwargs):
        return {
            "id": kwargs.get("id_") or str(self.account_model.id),
            "preferred_username": kwargs.get("id_") or str(self.account_model.id),
        }

    # noinspection PyMethodMayBeStatic
    def random_number(self, *args, **kwargs):
        return "098765"
