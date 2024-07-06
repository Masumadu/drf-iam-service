from core.repository import SqlBaseRepository

from .models import UserModel


class UserRepository(SqlBaseRepository):
    model = UserModel
    object_name = "user"
