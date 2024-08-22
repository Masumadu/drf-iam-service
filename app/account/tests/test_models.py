from django.test import tag

from app.account.models import AccountModel

from .base_test_case import AccountTestCase


@tag("app.account.model")
class TestUserModel(AccountTestCase):
    def test_user_model(self):
        self.assertEqual(AccountModel.objects.count(), 2)
        account = AccountModel.objects.get(pk=self.account_model.id)
        self.assertIsInstance(account, AccountModel)
        self.assertTrue(hasattr(account, "id"))
        self.assertTrue(hasattr(account, "username"))
        self.assertTrue(hasattr(account, "phone"))
        self.assertTrue(hasattr(account, "email"))
        self.assertTrue(hasattr(account, "password_expiry"))
        self.assertTrue(hasattr(account, "iam_provider_id"))
        self.assertTrue(hasattr(account, "is_email_verified"))
        self.assertTrue(hasattr(account, "is_phone_verified"))
        self.assertTrue(hasattr(account, "api_key"))
        self.assertTrue(hasattr(account, "api_key_enabled"))
        self.assertTrue(hasattr(account, "comment"))
        self.assertTrue(hasattr(account, "security_token"))
        self.assertTrue(hasattr(account, "status"))
        self.assertTrue(hasattr(account, "last_login"))
        self.assertTrue(hasattr(account, "is_staff"))
        self.assertTrue(hasattr(account, "is_active"))
        self.assertTrue(hasattr(account, "created_at"))
        self.assertTrue(hasattr(account, "created_by"))
        self.assertTrue(hasattr(account, "updated_at"))
        self.assertTrue(hasattr(account, "updated_by"))
        self.assertTrue(hasattr(account, "deleted_at"))
        self.assertTrue(hasattr(account, "deleted_by"))

    def test_create_user(self):
        account = AccountModel.objects.create_user(
            **self.account_test_data.create_account()
        )
        self.assertIsInstance(account, AccountModel)
