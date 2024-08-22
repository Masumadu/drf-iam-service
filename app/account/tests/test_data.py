from core.constants import GroupEnum


class AccountTestData:
    @property
    def existing_account(self):
        return {
            "phone": "1234556789",
            "email": "test@example.com",
            "username": "test_username",
            "secret": "test_password",
        }

    def create_account(self, email="example@example.com"):
        return {
            "phone": "test_phone",
            "email": email,
            "username": "new_username",
            "password": "new_password",
        }

    def login_account(self, password=None):
        return {
            "username": self.existing_account.get("username"),
            "password": password or self.existing_account.get("secret"),
        }

    def refresh_token(self, refresh_token):
        return {"refresh_token": refresh_token}

    def change_password(self, old_password=None):
        return {
            "old_password": old_password or self.existing_account.get("secret"),
            "new_password": "new_password",
        }

    def change_group(self, id_: str = None):
        return {"id": id_, "group": GroupEnum.admin.value}
