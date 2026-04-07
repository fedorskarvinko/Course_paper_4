from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email"""

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Обязательное поле. Используется для входа в систему.",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите изображение профиля",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон",
        help_text="Номер телефона в международном формате",
    )
    country = models.CharField(
        max_length=100, blank=True, verbose_name="Страна", help_text="Страна проживания"
    )

    # Меняем поле для авторизации с username на email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # username всё ещё нужен для админки

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]

    def __str__(self):
        return f"{self.email} ({self.get_full_name() or self.username})"
