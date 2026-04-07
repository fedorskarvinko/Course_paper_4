import os
import sys

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from mailing.models import Client, Mailing, Message


class Command(BaseCommand):
    help = 'Создает группу "Менеджеры" с необходимыми правами'

    def handle(self, *args, **options):
        # Создаем группу
        managers_group, created = Group.objects.get_or_create(name="Менеджеры")

        # Получаем все разрешения
        permissions = Permission.objects.filter(
            codename__in=[
                "view_client",
                "change_client",
                "delete_client",
                "view_message",
                "change_message",
                "delete_message",
                "view_mailing",
                "change_mailing",
                "delete_mailing",
                "view_mailingattempt",
                "can_view_all_clients",
                "can_deactivate_client",
                "can_view_all_messages",
                "can_edit_any_message",
                "can_view_all_mailings",
                "can_cancel_any_mailing",
            ]
        )

        # Назначаем права группе
        managers_group.permissions.set(permissions)

        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ Группа "Менеджеры" создана с правами')
            )
        else:
            self.stdout.write(self.style.SUCCESS('✅ Группа "Менеджеры" обновлена'))

        # Создаем также группу "Пользователи" с базовыми правами
        users_group, created = Group.objects.get_or_create(name="Пользователи")
        basic_permissions = Permission.objects.filter(
            codename__in=[
                "view_client",
                "add_client",
                "change_client",
                "delete_client",
                "view_message",
                "add_message",
                "change_message",
                "delete_message",
                "view_mailing",
                "add_mailing",
                "change_mailing",
                "delete_mailing",
                "view_mailingattempt",
            ]
        )
        users_group.permissions.set(basic_permissions)

        self.stdout.write(
            self.style.SUCCESS('✅ Группа "Пользователи" создана с базовыми правами')
        )
