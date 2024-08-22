from core.repository import SqlBaseRepository

from .models import AccountModel


class AccountRepository(SqlBaseRepository):
    model = AccountModel
    object_name = "account"
