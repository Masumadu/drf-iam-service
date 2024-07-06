from django.test import tag

from app.todo.models import TodoModel

from .base_test_case import BaseTestCase


@tag("app.todo.model")
class TestTodoModel(BaseTestCase):
    def test_todo_model(self):
        self.assertEqual(TodoModel.objects.count(), 1)
        todo = TodoModel.objects.get(pk=self.todo_model.id)
        self.assertIsInstance(todo, TodoModel)
        self.assertTrue(hasattr(todo, "id"))
        self.assertTrue(hasattr(todo, "todo"))
        self.assertTrue(hasattr(todo, "completed"))
        self.assertTrue(hasattr(todo, "user"))
        self.assertTrue(hasattr(todo, "created_at"))
        self.assertTrue(hasattr(todo, "created_by"))
        self.assertTrue(hasattr(todo, "updated_at"))
        self.assertTrue(hasattr(todo, "updated_by"))
        self.assertTrue(hasattr(todo, "deleted_at"))
        self.assertTrue(hasattr(todo, "deleted_by"))
