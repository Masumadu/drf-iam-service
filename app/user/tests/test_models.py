from django.test import tag

from app.user.models import UserModel

from .base_test_case import BaseTestCase


@tag("app.user.model")
class TestUserModel(BaseTestCase):
    def test_user_model(self):
        self.assertEqual(UserModel.objects.count(), 1)
        user = UserModel.objects.get(pk=self.user_model.id)
        self.assertIsInstance(user, UserModel)
        self.assertTrue(hasattr(user, "id"))
        self.assertTrue(hasattr(user, "name"))
        self.assertTrue(hasattr(user, "username"))
        self.assertTrue(hasattr(user, "password"))
        self.assertTrue(hasattr(user, "secret"))
        self.assertTrue(hasattr(user, "phone"))
        self.assertTrue(hasattr(user, "email"))
        self.assertTrue(hasattr(user, "is_staff"))
        self.assertTrue(hasattr(user, "is_active"))
        self.assertTrue(hasattr(user, "created_at"))
        self.assertTrue(hasattr(user, "created_by"))
        self.assertTrue(hasattr(user, "updated_at"))
        self.assertTrue(hasattr(user, "updated_by"))
        self.assertTrue(hasattr(user, "deleted_at"))
        self.assertTrue(hasattr(user, "deleted_by"))

    def test_create_user(self):
        user = UserModel.objects.create_user(**self.user_test_data.create_user())
        self.assertIsInstance(user, UserModel)

    def test_create_superuser(self):
        user = UserModel.objects.create_superuser(
            **self.user_test_data.create_superuser
        )
        self.assertIsInstance(user, UserModel)
