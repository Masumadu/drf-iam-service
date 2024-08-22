from unittest import mock
from urllib.parse import urlencode

from django.test import tag
from django.urls import reverse
from rest_framework import status

from .base_test_case import AccountTestCase


@tag("app.account.view")
class TestAccountView(AccountTestCase):
    def test_view_all_accounts(self):
        self.jwt_decode.return_value = self.mock_decode_token(
            id_=self.super_admin_model.id
        )
        query_params = {"page": 1, "page_size": 1}
        response = self.client.get(
            f"{reverse('view_all_accounts')}?{urlencode(query_params)}",
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)
        self.assertIn("count", response_data)
        self.assertIn("next", response_data)
        self.assertIn("previous", response_data)
        self.assertIsInstance(response_data.get("results"), list)
        self.assertEqual(
            len(response_data.get("results")), query_params.get("page_size")
        )

    def test_get_all_account_unauthorized_exc(self):
        response = self.client.get(
            f"{reverse('view_all_accounts')}?{urlencode({'page': 1, 'page_size': 1})}"
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_get_all_account_permission_exc(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        response = self.client.get(
            f"{reverse('view_all_accounts')}?{urlencode({'page': 1, 'page_size': 1})}",
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIsInstance(response_data, dict)

    def test_get_account(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        response = self.client.get(reverse("get_account"), headers=self.headers)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_get_account_unauthorized_exc(self):
        response = self.client.get(reverse("get_account"))
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    @mock.patch("core.services.keycloak_service.KeycloakAuthService.create_user")
    def test_create_account(self, mock_create_user):
        mock_create_user.return_value = self.mock_keycloak_auth.create_user()
        response = self.client.post(
            reverse("create_account"),
            data=self.account_test_data.create_account(),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(response_data, dict)

    def test_create_account_invalid_data_exc(self):
        response = self.client.post(
            reverse("create_account"),
            data=self.account_test_data.create_account(email="invalid"),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_verify_account_email(self):
        base_url = reverse("verify_account_email")
        query_params = {"token": self.access_token}
        url_with_query = f"{base_url}?{urlencode(query_params)}"
        response = self.client.get(url_with_query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resend_email_verification(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        response = self.client.get(
            reverse("resend_email_verification"), headers=self.headers
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_verify_account_phone(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        self.client.get(
            f"{reverse('send_one_time_password')}?{urlencode({'phone': self.account_model.phone})}"  # noqa
        )
        response = self.client.get(
            f"{reverse('verify_account_phone')}?{urlencode({'verification_code': self.random_number()})}",  # noqa
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_apikey(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        response = self.client.get(reverse("generate_api_key"), headers=self.headers)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_get_account_by_apikey(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        apikey = self.client.get(reverse("generate_api_key"), headers=self.headers)
        response = self.client.get(
            reverse(
                "get_account_by_apikey", kwargs={"apikey": apikey.json().get("apikey")}
            ),
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_toggle_apikey_status(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        self.client.get(reverse("generate_api_key"), headers=self.headers)
        response = self.client.get(
            reverse("toggle_apikey_status"), headers=self.headers
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    @mock.patch("core.services.keycloak_service.KeycloakAuthService.get_token")
    @mock.patch("core.services.keycloak_service.KeycloakAuthService.create_user")
    def test_login_account(self, mock_create_user, mock_get_token):
        mock_create_user.return_value = self.mock_keycloak_auth.create_user()
        mock_get_token.return_value = self.mock_keycloak_auth.get_token()
        response = self.client.post(
            reverse("login_account"),
            data=self.account_test_data.login_account(),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_login_account_invalid_credential_exc(self):
        response = self.client.post(
            reverse("login_account"),
            data=self.account_test_data.login_account(password="invalid"),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response_data, dict)

    @mock.patch("core.services.keycloak_service.KeycloakAuthService.refresh_token")
    def test_refresh_token(self, mock_refresh_token):
        mock_refresh_token.return_value = self.mock_keycloak_auth.get_token()
        response = self.client.post(
            reverse("refresh_access_token"),
            data=self.account_test_data.refresh_token(self.refresh_token),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_reset_password_request(self):
        response = self.client.get(
            f"{reverse('reset_password_request')}?{urlencode({'phone': self.account_model.phone})}",  # noqa
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    @mock.patch("core.services.keycloak_service.KeycloakAuthService.change_password")
    def test_reset_password(self, mock_change_password):
        mock_change_password.return_value = self.mock_keycloak_auth.change_password()
        self.client.get(
            f"{reverse('send_one_time_password')}?{urlencode({'phone': self.account_model.phone})}"  # noqa
        )
        otp = self.client.post(
            reverse("confirm_one_time_password"),
            data={"id": self.account_model.id, "otp_code": self.random_number()},
            format=self.data_format,
        )
        response = self.client.post(
            reverse("reset_password"),
            data={
                "id": self.account_model.id,
                "new_password": "password",
                "sec_code": otp.json().get("sec_code"),
            },
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    @mock.patch("core.services.keycloak_service.KeycloakAuthService.get_token")
    @mock.patch("core.services.keycloak_service.KeycloakAuthService.change_password")
    def test_change_password(self, mock_change_password, mock_get_token):
        self.jwt_decode.return_value = self.mock_decode_token()
        mock_change_password.return_value = self.mock_keycloak_auth.change_password()
        mock_get_token.return_value = self.mock_keycloak_auth.get_token()
        response = self.client.post(
            reverse("change_password"),
            data=self.account_test_data.change_password(),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_change_password_invalid_data_exc(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        response = self.client.post(
            reverse("change_password"),
            data=self.account_test_data.change_password().pop("old_password"),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_change_user_password_unauthorized_exc(self):
        response = self.client.post(
            reverse("change_password"),
            data=self.account_test_data.change_password(),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_change_password_invalid_credential_exc(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        response = self.client.post(
            reverse("change_password"),
            data=self.account_test_data.change_password(old_password="invalid"),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response_data, dict)

    def test_send_one_time_password(self):
        response = self.client.get(
            f"{reverse('send_one_time_password')}?{urlencode({'phone': self.account_model.phone})}"  # noqa
        )

        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_confirm_one_time_password(self):
        self.client.get(
            f"{reverse('send_one_time_password')}?{urlencode({'phone': self.account_model.phone})}"  # noqa
        )
        response = self.client.post(
            reverse("confirm_one_time_password"),
            data={"id": self.account_model.id, "otp_code": self.random_number()},
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_deactivate_account(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        response = self.client.delete(
            reverse("deactivate_account"), headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deactivate_account_unauthorized_exc(self):
        response = self.client.delete(reverse("deactivate_account"))
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_update_group(self):
        self.jwt_decode.return_value = self.mock_decode_token(
            id_=self.super_admin_model.id
        )
        response = self.client.patch(
            reverse("update_account_group"),
            data=self.account_test_data.change_group(str(self.account_model.id)),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_update_group_invalid_data_exc(self):
        self.jwt_decode.return_value = self.mock_decode_token(
            id_=self.super_admin_model.id
        )
        response = self.client.patch(
            reverse("update_account_group"),
            data=self.account_test_data.change_group(),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_update_group_unauthorized_exc(self):
        response = self.client.patch(
            reverse("update_account_group"),
            data=self.account_test_data.change_group(),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_update_group_permission_exc(self):
        self.jwt_decode.return_value = self.mock_decode_token()
        response = self.client.patch(
            reverse("update_account_group"),
            data=self.account_test_data.change_group(self.account_model.id),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIsInstance(response_data, dict)
