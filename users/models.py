from django.conf import settings
from django.db import models


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
