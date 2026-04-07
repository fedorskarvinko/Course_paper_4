from django.core.cache import cache
from django.db import models

from config import settings


class Client(models.Model):
    owner = models.ForeignKey(  # ДОБАВЛЕНО ПОЛЕ
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        permissions = [
            ("can_view_all_clients", "Может просматривать всех клиентов"),
            ("can_deactivate_client", "Может деактивировать клиента"),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    owner = models.ForeignKey(  # ДОБАВЛЕНО ПОЛЕ
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("can_view_all_messages", "Может просматривать все сообщения"),
            ("can_edit_any_message", "Может редактировать любые сообщения"),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    owner = models.ForeignKey(  # ДОБАВЛЕНО ПОЛЕ
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    clients = models.ManyToManyField(Client, verbose_name="Получатели")

    def __str__(self):
        return f"Рассылка #{self.id} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, verbose_name="Рассылка"
    )
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус попытки"
    )
    server_response = models.TextField(blank=True, verbose_name="Ответ сервера")

    def __str__(self):
        return f"Попытка #{self.id} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("can_view_all_mailings", "Может просматривать все рассылки"),
            ("can_cancel_any_mailing", "Может отменять любые рассылки"),
        ]


def clear_client_cache(sender, instance, **kwargs):
    """Очистка кеша при изменении клиентов"""
    cache.delete("home_stats")


def clear_mailing_cache(sender, instance, **kwargs):
    """Очистка кеша при изменении рассылок"""
    cache.delete("home_stats")


from django.db.models.signals import post_delete, post_save

post_save.connect(clear_client_cache, sender=Client)
post_delete.connect(clear_client_cache, sender=Client)

post_save.connect(clear_mailing_cache, sender=Mailing)
post_delete.connect(clear_mailing_cache, sender=Mailing)
