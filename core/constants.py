import enum


class AccountStatusEnum(enum.Enum):
    inactive = "inactive"
    active = "active"
    disabled = "disabled"
    blocked = "blocked"
    deactivated = "deactivated"


class GroupEnum(enum.Enum):
    user = "user"
    admin = "admin"
    super_admin = "super_admin"
