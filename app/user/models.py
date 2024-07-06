import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

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


class UserModel(BaseModel, AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(null=False, max_length=255)
    username = models.CharField(null=False, unique=True, db_index=True, max_length=255)
    phone = models.CharField(null=False, unique=True, db_index=True, max_length=255)
    email = models.EmailField(null=False, unique=True, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "username"
    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["created_at"]

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.username

    @property
    def secret(self):
        return self.password

    @secret.setter
    def secret(self, value):
        self.password = make_password(value)
