from django.test import tag
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.request import Request

from app.todo.serializer import TodoSerializer
from core.exceptions import AppException

from .base_test_case import BaseTestCase


@tag("app.todo.controller")
class TestTodoController(BaseTestCase):
    def test_view_all_todos(self):
        request = Request(
            self.request_factory.get(self.request_url, data={"page": 1, "page_size": 1})
        )
        results = self.todo_controller.view_all_todos(request)
        self.assertEqual(results.status_code, 200)
        self.assertIsInstance(results.data, dict)
        self.assertIsInstance(results.data.get("results"), list)
        self.assertEqual(
            len(results.data.get("results")), int(request.query_params.get("page_size"))
        )

    def test_create_todo(self):
        request = Request(
            self.request_factory.post(
                self.request_url,
                self.todo_test_data.create_todo,
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        request.user = self.user_model
        result = self.todo_controller.create_todo(request)
        self.assertIsInstance(result, TodoSerializer)
        self.assertIsInstance(result.data, dict)

    def test_create_todo_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.todo_test_data.create_todo.pop("todo"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            request.user = self.user_model
            self.todo_controller.create_todo(request)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_get_todo(self):
        result = self.todo_controller.get_todo(self.todo_model.id)
        self.assertIsInstance(result, TodoSerializer)
        self.assertIsInstance(result.data, dict)

    def test_get_todo_not_found_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            self.todo_controller.get_todo(self.user_model.id)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_update_todo(self):
        request = Request(
            self.request_factory.post(
                self.request_url,
                self.todo_test_data.update_todo(),
                format=self.data_format,
            ),
            parsers=[JSONParser()],
        )
        result = self.todo_controller.update_todo(request, self.todo_model.id)
        self.assertIsInstance(result, TodoSerializer)
        self.assertIsInstance(result.data, dict)

    def test_update_todo_invalid_data_exc(self):
        with self.assertRaises(AppException.ValidationException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.todo_test_data.update_todo(completed="invalid"),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.todo_controller.update_todo(request, self.todo_model.id)
        self.assertEqual(
            exception.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertIsNotNone(exception.exception.error_message)

    def test_update_todo_notfound_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            request = Request(
                self.request_factory.post(
                    self.request_url,
                    self.todo_test_data.update_todo(),
                    format=self.data_format,
                ),
                parsers=[JSONParser()],
            )
            self.todo_controller.update_todo(request, self.user_model.id)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)

    def test_delete_todo(self):
        result = self.todo_controller.delete_todo(self.todo_model.id)
        self.assertIsNone(result)

    def test_delete_todo_not_found_exc(self):
        with self.assertRaises(AppException.NotFoundException) as exception:
            self.todo_controller.delete_todo(self.user_model.id)
        self.assertEqual(exception.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(exception.exception.error_message)
