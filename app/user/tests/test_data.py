class UserTestData:
    @property
    def existing_user(self):
        return {
            "phone": "1234556789",
            "email": "test@example.com",
            "username": "test_username",
            "secret": "test_password",
        }

    def create_user(self, email="example@example.com"):
        return {
            "name": "test_name",
            "phone": "test_phone",
            "email": email,
            "username": "new_username",
            "password": "new_password",
        }

    @property
    def create_superuser(self):
        return {"username": "new_username", "password": "new_password"}

    def update_user(self, email="example@example.com"):
        return {"email": email}

    def login_user(self, password=None):
        return {
            "username": self.existing_user.get("username"),
            "password": password or self.existing_user.get("secret"),
        }

    def refresh_token(self, refresh_token):
        return {"refresh_token": refresh_token}

    def change_password(self, old_password=None):
        return {
            "old_password": old_password or self.existing_user.get("secret"),
            "new_password": "new_password",
        }
