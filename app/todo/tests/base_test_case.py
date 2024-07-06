from app.todo.controller import TodoController
from app.todo.models import TodoModel
from app.todo.repository import TodoRepository
from app.user.tests import BaseTestCase as UserBaseTestCase

from .test_data import TodoTestData


class BaseTestCase(UserBaseTestCase):
    def setup_test_data(self):
        super().setup_test_data()
        self.todo_test_data = TodoTestData()
        self.todo_model = TodoModel.objects.create(
            **self.todo_test_data.existing_todo(self.user_model.id)
        )

    def instantiate_classes(self):
        """This is where all classes are instantiated for the test"""
        super().instantiate_classes()
        self.todo_repository = TodoRepository()
        self.todo_controller = TodoController(
            todo_repository=self.todo_repository, user_repository=self.user_repository
        )
