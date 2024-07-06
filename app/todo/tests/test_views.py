from urllib.parse import urlencode

from django.test import tag
from django.urls import reverse
from rest_framework import status

from .base_test_case import BaseTestCase


@tag("app.todo.view")
class TestTodoView(BaseTestCase):
    def test_view_all_todos(self):
        base_url = reverse("view_all_todos")
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

    def test_create_todo(self):
        response = self.client.post(
            reverse("create_todo"),
            data=self.todo_test_data.create_todo,
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(response_data, dict)

    def test_create_user_invalid_data_exc(self):
        response = self.client.post(
            reverse("create_todo"),
            data=self.todo_test_data.create_todo.update(
                self.todo_test_data.update_todo()
            ),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_create_todo_unauthorized_exc(self):
        response = self.client.post(
            reverse("create_todo"),
            data=self.todo_test_data.create_todo,
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_get_todo(self):
        response = self.client.get(
            reverse("get_todo", args=[self.todo_model.id]), headers=self.headers
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_get_todo_unauthorized_exc(self):
        response = self.client.get(reverse("get_todo", args=[self.todo_model.id]))
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_get_todo_notfound_exc(self):
        response = self.client.get(
            reverse("get_todo", args=[self.user_model.id]), headers=self.headers
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response_data, dict)

    def test_update_update(self):
        response = self.client.patch(
            reverse("update_todo", args=[self.todo_model.id]),
            data=self.todo_test_data.update_todo(),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)

    def test_update_todo_invalid_data_exc(self):
        response = self.client.patch(
            reverse("update_todo", args=[self.todo_model.id]),
            data=self.todo_test_data.update_todo("update"),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIsInstance(response_data, dict)

    def test_update_todo_unauthorized_exc(self):
        response = self.client.patch(
            reverse("update_todo", args=[self.todo_model.id]),
            data=self.todo_test_data.update_todo(),
            format=self.data_format,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_update_todo_notfound_exc(self):
        response = self.client.patch(
            reverse("update_todo", args=[self.user_model.id]),
            data=self.todo_test_data.update_todo(),
            format=self.data_format,
            headers=self.headers,
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response_data, dict)

    def test_delete_todo(self):
        response = self.client.delete(
            reverse("delete_todo", args=[self.todo_model.id]), headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_todo_unauthorized_exc(self):
        response = self.client.delete(reverse("delete_todo", args=[self.todo_model.id]))
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsInstance(response_data, dict)

    def test_delete_todo_notfound_exc(self):
        response = self.client.delete(
            reverse("delete_todo", args=[self.user_model.id]), headers=self.headers
        )
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response_data, dict)
