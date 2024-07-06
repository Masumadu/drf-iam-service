from django.test import tag
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.request import Request

from app.user.serializer import UserSerializer
from core.exceptions import AppException

from .base_test_case import BaseTestCase


@tag("app.user.controller")
class TestUserController(BaseTestCase):
    def test_view_all_users(self):
        request = Request(
            self.request_factory.get(self.request_url, data={"page": 1, "page_size": 1})
        )
        results = self.user_controller.view_all_users(request)
        self.assertEqual(results.status_code, 200)
        self.assertIsInstance(results.data, dict)
        self.assertIsInstance(results.data.get("results"), list)
        self.assertEqual(
            len(results.data.get("results")), int(request.query_params.get("page_size"))
        )

    def test_create_user(self):
        result = self.user_controller.create_user(
            obj_data=self.user_test_data.create_user()
        )
        self.assertIsInstance(result, UserSerializer)
        self.assertIsInstance(result.data, dict)

    def test_create_user_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            self.user_controller.create_user(
                obj_data=self.user_test_data.create_user(email="invalid")
            )
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_get_user(self):
        request = Request(self.request_factory.get(self.request_url))
        request.user = self.user_model
        result = self.user_controller.get_user(request)
        self.assertIsInstance(result, UserSerializer)
        self.assertIsInstance(result.data, dict)

    def test_get_user_not_found_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            request = Request(self.request_factory.get(self.request_url))
            self.user_controller.get_user(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_update_user(self):
        request = Request(
            self.request_factory.post(
                self.request_url,
                self.user_test_data.update_user(),
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        request.user = self.user_model
        result = self.user_controller.update_user(request)
        self.assertIsInstance(result, UserSerializer)
        self.assertIsInstance(result.data, dict)

    def test_update_user_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.user_test_data.update_user(email="invalid"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            request.user = self.user_model
            self.user_controller.update_user(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_delete_user(self):
        request = Request(self.request_factory.get(self.request_url))
        request.user = self.user_model
        result = self.user_controller.delete_user(request)
        self.assertIsNone(result)

    def test_delete_user_not_found_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            request = Request(self.request_factory.get(self.request_url))
            self.user_controller.delete_user(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_get_token(self):
        result = self.user_controller.get_token(self.user_model)
        self.assertIsInstance(result, dict)

    def test_refresh_token(self):
        token = self.user_controller.get_token(self.user_model)
        result = self.user_controller.refresh_token(token.get("refresh_token"))
        self.assertIsInstance(result, dict)

    def test_refresh_token_invalid_exc(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            self.user_controller.refresh_token(self.access_token)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_login_user(self):
        request = Request(
            self.request_factory.post(
                self.request_url,
                self.user_test_data.login_user(),
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        result = self.user_controller.login_user(request)
        self.assertIsInstance(result, dict)

    def test_login_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.user_test_data.login_user().pop("username"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.user_controller.login_user(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_login_user_invalid_credential_exc(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.user_test_data.login_user(password="invalid"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.user_controller.login_user(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_refresh_user_token(self):
        token = self.user_controller.get_token(self.user_model)
        request = Request(
            self.request_factory.post(
                self.request_url,
                self.user_test_data.refresh_token(token.get("refresh_token")),
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        result = self.user_controller.refresh_user_token(request)
        self.assertIsInstance(result, dict)

    def test_refresh_user_token_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.user_test_data.refresh_token(self.refresh_token).update(
                        self.user_test_data.existing_user
                    ),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.user_controller.refresh_user_token(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_change_user_password(self):
        request = Request(
            self.request_factory.post(
                self.request_url,
                self.user_test_data.change_password(),
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        request.user = self.user_model
        result = self.user_controller.change_user_password(request)
        self.assertIsInstance(result, dict)

    def test_change_user_password_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.user_test_data.change_password().pop("old_password"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            request.user = self.user_model
            self.user_controller.change_user_password(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_change_user_password_invalid_password_exc(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.user_test_data.change_password(old_password="invalid"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            request.user = self.user_model
            self.user_controller.change_user_password(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)
