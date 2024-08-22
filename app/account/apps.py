from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.account"

    def ready(self):
        from app.account import signal  # noqa
