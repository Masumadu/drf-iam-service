from urllib.parse import urlencode

from django.test import tag
from django.urls import reverse
from rest_framework import status

from .base_test_case import BaseTestCase


@tag("app.user.view")
class TestUserView(BaseTestCase):
    def test_view_all_users(self):
        base_url = reverse("view_all_users")
        query_params = {"page": 1, "page_size": 1}
        url_with_query = f"{base_url}?{urlencode(query_params)}"
        response = self.client.get(url_with_query, headers=self.headers)
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

    def test_view_all_users_unauthorized_exc(self):
        base_url = reverse("view_all_users")
        query_params = {"page": 1, "page_size": 1}
        url_with_query = f"{base_url}?{urlencode(query_params)}"
        response = self.client.get(url_with_query)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user(self):
        response = self.client.post(
            reverse("create_user"),
            data=self.user_test_data.create_user(),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(response_data, dict)

    def test_create_user_invalid_data_exc(self):
        response = self.client.post(
            reverse("create_user"),
            data=self.user_test_data.create_user(email="invalid"),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_get_user(self):
        response = self.client.get(reverse("get_user"), headers=self.headers)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_get_user_unauthorized_exc(self):
        response = self.client.get(reverse("get_user"))
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_update_user(self):
        response = self.client.patch(
            reverse("update_user"),
            data=self.user_test_data.update_user(),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_update_user_invalid_data_exc(self):
        response = self.client.patch(
            reverse("update_user"),
            data=self.user_test_data.update_user(email="invalid"),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_update_user_unauthorized_exc(self):
        response = self.client.patch(
            reverse("update_user"),
            data=self.user_test_data.update_user(),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_delete_user(self):
        response = self.client.delete(reverse("delete_user"), headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_unauthorized_exc(self):
        response = self.client.delete(reverse("delete_user"))
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_login_user(self):
        response = self.client.post(
            reverse("login_user"),
            data=self.user_test_data.login_user(),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_login_user_invalid_data_exc(self):
        response = self.client.post(
            reverse("login_user"),
            data=self.user_test_data.login_user().pop("username"),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_login_user_invalid_credential_exc(self):
        response = self.client.post(
            reverse("login_user"),
            data=self.user_test_data.login_user(password="invalid"),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response_data, dict)

    def test_refresh_user_token(self):
        response = self.client.post(
            reverse("refresh_user_token"),
            data=self.user_test_data.refresh_token(refresh_token=self.refresh_token),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_refresh_user_token_invalid_data_exc(self):
        response = self.client.post(
            reverse("login_user"),
            data=self.user_test_data.refresh_token(self.refresh_token).update(
                self.user_test_data.login_user()
            ),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_refresh_user_token_invalid_refresh_token_exc(self):
        response = self.client.post(
            reverse("refresh_user_token"),
            data=self.user_test_data.refresh_token(refresh_token=self.access_token),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response_data, dict)

    def test_change_user_password(self):
        response = self.client.post(
            reverse("change_user_password"),
            data=self.user_test_data.change_password(),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_change_user_password_invalid_data_exc(self):
        response = self.client.post(
            reverse("change_user_password"),
            data=self.user_test_data.change_password().pop("old_password"),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_change_user_password_unauthorized_exc(self):
        response = self.client.post(
            reverse("change_user_password"),
            data=self.user_test_data.change_password(),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_change_user_password_invalid_credential_exc(self):
        response = self.client.post(
            reverse("change_user_password"),
            data=self.user_test_data.change_password(old_password="invalid"),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response_data, dict)
