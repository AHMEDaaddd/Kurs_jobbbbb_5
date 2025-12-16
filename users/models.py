from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class TelegramProfile(models.Model):
    """
    Профиль пользователя для интеграции с Telegram.
    Храним chat_id для отправки напоминаний.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
        verbose_name="Пользователь",
    )
    chat_id = models.CharField(
        "Telegram chat_id",
        max_length=64,
        unique=True,
    )

    def __str__(self) -> str:
        return f"Telegram профиль {self.user} ({self.chat_id})"


class User(AbstractUser):
    """Custom user model based on AbstractUser."""
    telegram_chat_id = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="Telegram chat_id for notifications",
    )