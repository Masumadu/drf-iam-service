import uuid
from unittest import mock

from django.conf import settings
from django.test import tag
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.request import Request

from app.account.models import AccountModel
from app.account.serializer import AccountSerializer
from core.exceptions import AppException

from .base_test_case import AccountTestCase


@tag("app.account.controller")
class TestAccountController(AccountTestCase):
    def test_view_all_accounts(self):
        request = Request(
            self.request_factory.get(self.request_url, data={"page": 1, "page_size": 1})
        )
        results = self.account_controller.view_all_accounts(request)
        self.assertEqual(results.status_code, 200)
        self.assertIsInstance(results.data, dict)
        self.assertIsInstance(results.data.get("results"), list)
        self.assertEqual(
            len(results.data.get("results")), int(request.query_params.get("page_size"))
        )

    def test_get_account(self):
        request = Request(self.request_factory.get(self.request_url))
        request.user = self.account_model
        results = self.account_controller.get_account(request)
        self.assertIsInstance(results, AccountSerializer)
        self.assertIsInstance(results.data, dict)

    def test_get_account_not_found_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            request = Request(self.request_factory.get(self.request_url))
            self.account_controller.get_account(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_create_account(self):
        result = self.account_controller.create_account(
            obj_data=self.account_test_data.create_account(),
            verification_url="https://example.com",
        )
        self.assertIsInstance(result, AccountSerializer)
        self.assertIsInstance(result.data, dict)

    def test_create_account_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            self.account_controller.create_account(
                obj_data=self.account_test_data.create_account(email="invalid"),
                verification_url="https://example.com",
            )
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_send_verification_link(self):
        result = self.account_controller.send_account_verification_link(
            user_id=self.account_model.id,
            url="http",
        )
        self.assertIsInstance(result, AccountSerializer)

    def test_send_verification_link_account_notfound_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            self.account_controller.send_account_verification_link(
                user_id=str(uuid.uuid4()),
                url="http",
            )
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_send_verification_link_account_verified_exc(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            self.account_repository.update_by_id(
                obj_id=self.account_model.id, obj_data={"is_email_verified": True}
            )
            self.account_controller.send_account_verification_link(
                user_id=self.account_model.id,
                url="http",
            )
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_generate_token(self):
        result = self.account_controller.generate_token(
            payload=self.account_test_data.existing_account
        )
        self.assertIsNotNone(result)

    @mock.patch("app.account.controller.jwt.decode")
    def test_decode_token(self, mock_jwt):
        mock_jwt.return_value = self.mock_decode_token(id_=self.account_model.id)
        result = self.account_controller.decode_token(token=self.access_token)
        self.assertIsNotNone(result)

    def test_decode_token_invalid(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            self.account_controller.decode_token(token=self.access_token)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    @mock.patch("app.account.controller.jwt.decode")
    def test_verify_email(self, mock_jwt):
        mock_jwt.return_value = self.mock_decode_token(id_=self.account_model.id)
        result = self.account_controller.verify_account_email(token=self.access_token)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, AccountModel)

    def test_verify_email_invalid_token(self):
        result = self.account_controller.verify_account_email(token=self.access_token)
        self.assertIsNone(result)

    @mock.patch("app.account.controller.jwt.decode")
    def test_verify_email_account_notfound_exc(self, mock_jwt):
        mock_jwt.return_value = self.mock_decode_token(id_=str(uuid.uuid4()))
        result = self.account_controller.verify_account_email(token=self.access_token)
        self.assertIsNone(result)

    def test_verify_phone(self):
        self.account_controller.send_otp(phone=self.account_model.phone)
        request = Request(
            self.request_factory.get(
                self.request_url,
                data={"verification_code": settings.MASTER_OTP_CODES[0]},
            )
        )
        request.user = self.account_model
        result = self.account_controller.verify_account_phone(request)
        self.assertIsInstance(result, AccountSerializer)

    def test_verify_phone_account_not_found(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            request = Request(
                self.request_factory.get(
                    self.request_url,
                    data={"verification_code": settings.MASTER_OTP_CODES[0]},
                )
            )
            self.account_controller.verify_account_phone(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_verify_phone_invalid_otp(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            request = Request(
                self.request_factory.get(
                    self.request_url, data={"verification_code": "invalid"}
                )
            )
            request.user = self.account_model
            self.account_controller.verify_account_phone(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_generate_api_key(self):
        request = Request(self.request_factory.get(self.request_url))
        request.user = self.account_model
        result = self.account_controller.generate_account_apikey(request)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_generate_api_key_account_notfound_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            request = Request(self.request_factory.get(self.request_url))
            request.user.id = str(uuid.uuid4())
            self.account_controller.generate_account_apikey(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_get_account_by_apikey(self):
        request = Request(self.request_factory.get(self.request_url))
        request.user = self.account_model
        response = self.account_controller.generate_account_apikey(request)
        result = self.account_controller.get_account_by_apikey(
            apikey=response.get("apikey")
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, AccountSerializer)

    def test_get_account_by_apikey_notfound_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            self.account_controller.get_account_by_apikey(
                apikey="-Y-cU0FkQbx9SkWhcpSX6GKL8EvvwszrEc0SXXdHghk"
            )
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_toggle_api_key_status(self):
        request = Request(self.request_factory.get(self.request_url))
        request.user = self.account_model
        self.account_controller.generate_account_apikey(request)
        result = self.account_controller.toggle_account_apikey_status(request)
        self.assertIsInstance(result, AccountSerializer)

    def test_toggle_api_key_status_notfound_exc(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            request = Request(self.request_factory.get(self.request_url))
            request.user = self.account_model
            self.account_controller.toggle_account_apikey_status(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_login_user(self):
        request = Request(
            self.request_factory.post(
                self.request_url,
                self.account_test_data.login_account(),
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        result = self.account_controller.login_account(request)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_login_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.account_test_data.login_account().pop("username"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.account_controller.login_account(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_login_user_invalid_credential_exc(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.account_test_data.login_account(password="invalid"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.account_controller.login_account(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_refresh_user_token(self):
        request = Request(
            self.request_factory.post(
                self.request_url,
                self.account_test_data.refresh_token(self.refresh_token),
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        result = self.account_controller.refresh_user_token(request)
        self.assertIsInstance(result, dict)

    def test_refresh_user_token_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.account_test_data.refresh_token(self.refresh_token).update(
                        self.account_test_data.existing_account
                    ),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.account_controller.refresh_user_token(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_reset_password_request(self):
        result = self.account_controller.reset_account_password_request(
            email=self.account_model.email, phone=self.account_model.phone
        )
        self.assertIsInstance(result, AccountSerializer)

    def test_reset_password_request_notfound_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            self.account_controller.reset_account_password_request(
                email="invalid@example.com", phone=None
            )
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_reset_password(self):
        self.account_controller.send_otp(phone=self.account_model.phone)
        otp_confirmation = self.account_controller.confirm_otp(
            account_id=self.account_model.id, otp_code=settings.MASTER_OTP_CODES[0]
        )
        request = Request(
            self.request_factory.post(
                self.request_url,
                {
                    "id": self.account_model.id,
                    "sec_code": otp_confirmation.get("sec_code"),
                    "new_password": "password",
                },
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        result = self.account_controller.reset_account_password(request)
        self.assertIsInstance(result, AccountSerializer)

    def test_reset_password_invalid_sec_code_exc(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    {
                        "id": self.account_model.id,
                        "sec_code": "sec_code",
                        "new_password": "password",
                    },
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.account_controller.reset_account_password(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_change_user_password(self):
        request = Request(
            self.request_factory.post(
                self.request_url,
                self.account_test_data.change_password(),
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        request.user = self.account_model
        result = self.account_controller.change_account_password(request)
        self.assertIsInstance(result, dict)

    def test_change_user_password_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.account_test_data.change_password().pop("old_password"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            request.user = self.account_model
            self.account_controller.change_account_password(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_change_user_password_invalid_password_exc(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.account_test_data.change_password(old_password="invalid"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            request.user = self.account_model
            self.account_controller.change_account_password(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_deactivate_account(self):
        request = Request(self.request_factory.get(self.request_url))
        request.user = self.account_model
        result = self.account_controller.deactivate_account(request)
        self.assertIsNone(result)

    def test_deactivate_account_not_found_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            request = Request(self.request_factory.get(self.request_url))
            request.user.id = str(uuid.uuid4())
            self.account_controller.deactivate_account(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_send_otp(self):
        result = self.account_controller.send_otp(email=self.account_model.email)
        self.assertIsInstance(result, AccountSerializer)

    def test_send_otp_invalid_channel(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            self.account_controller.send_otp()
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_confirm_otp(self):
        request = Request(
            self.request_factory.post(
                path=self.request_url,
                data={"id": self.account_model.id, "otp_code": self.random_number()},
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        self.account_controller.send_otp(email=self.account_model.email)
        result = self.account_controller.otp_confirmation(request)
        self.assertIsInstance(result, dict)

    def test_confirm_otp_invalid_data(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    path=self.request_url,
                    data={"id": self.account_model.id},
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.account_controller.otp_confirmation(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_confirm_otp_invalid_code(self):
        with self.assertRaises(AppException.BadRequestException) as exception:
            request = Request(
                self.request_factory.post(
                    path=self.request_url,
                    data={"id": self.account_model.id, "otp_code": "invalid"},
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.account_controller.otp_confirmation(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(exception.exception.error_message)

    def test_update_account_group(self):
        request = Request(
            self.request_factory.post(
                path=self.request_url,
                data=self.account_test_data.change_group(
                    str(self.super_admin_model.id)
                ),
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        result = self.account_controller.update_group(request)
        self.assertIsInstance(result, AccountSerializer)

    def test_update_account_group_invalid_data(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    path=self.request_url,
                    data=self.account_test_data.change_group(),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.account_controller.update_group(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_update_account_group_notfound_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            request = Request(
                self.request_factory.post(
                    path=self.request_url,
                    data=self.account_test_data.change_group(str(uuid.uuid4())),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.account_controller.update_group(request)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)
