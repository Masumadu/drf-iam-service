from core.repository import SqlBaseRepository

from .models import TodoModel


class TodoRepository(SqlBaseRepository):
    model = TodoModel
    object_name = "todo"
