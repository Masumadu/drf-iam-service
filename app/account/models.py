import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.exceptions import AppException
from core.models import BaseModel


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("User must have a username")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(username, password, **extra_fields)


class AccountModel(BaseModel, AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    username = models.CharField(null=False, unique=True, db_index=True, max_length=255)
    phone = models.CharField(null=False, unique=True, db_index=True, max_length=255)
    email = models.EmailField(null=False, unique=True, db_index=True)
    password_expiry = models.DateTimeField(null=True)
    iam_provider_id = models.CharField(null=True)
    is_email_verified = models.BooleanField(null=False, default=False)
    is_phone_verified = models.BooleanField(null=False, default=False)
    api_key = models.CharField(null=True)
    api_key_enabled = models.BooleanField(null=True, default=False)
    comment = models.JSONField(null=True)
    security_token = models.CharField(null=True)
    security_token_expiration = models.DateTimeField(null=True)
    status = models.CharField(null=False)
    last_login = models.DateTimeField(null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "username"
    objects = UserManager()

    class Meta:
        db_table = "user_accounts"
        ordering = ["created_at"]

    def __str__(self):
        return f"UserAccount{self.username, self.phone}"

    def __repr__(self):
        return f"UserAccount{self.username, self.phone}"

    @property
    def secret(self):
        return self.password

    @secret.setter
    def secret(self, value):
        self.password = make_password(value)

    @classmethod
    def hash_apikey(cls, value: str):
        try:
            return make_password(value, salt=cls.gen_salt(value))
        except Exception as exc:
            raise AppException.BadRequestException("api key invalid") from exc

    @classmethod
    def gen_salt(cls, value: str):
        salt = "".join(char for char in value if char not in ["-", "_"])
        return f"{salt[-21:]}e"
