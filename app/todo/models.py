import uuid

from django.db import models

from app.user.models import UserModel
from core.models import BaseModel

# Create your models here.


class TodoModel(BaseModel):
    id = models.UUIDField(null=False, primary_key=True, default=uuid.uuid4)
    todo = models.TextField(null=False)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(to=UserModel, on_delete=models.CASCADE)

    class Meta:
        db_table = "todos"
        ordering = ["created_at"]

    def __str__(self):
        return self.todo

    def __repr__(self):
        return self.todo
