from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from core.constants import GroupEnum


def create_groups():
    for group in [data.value for data in GroupEnum]:
        Group.objects.get_or_create(name=group)
    return None


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        create_groups()
        super_admin = User.objects.create_superuser(
            username=settings.SUPER_ADMIN_USERNAME,
            email=settings.SUPER_ADMIN_EMAIL,
            password=settings.SUPER_ADMIN_PASSWORD,
            phone=settings.SUPER_ADMIN_PHONE,
        )
        super_admin.groups.add(Group.objects.get(name=GroupEnum.super_admin.value))
