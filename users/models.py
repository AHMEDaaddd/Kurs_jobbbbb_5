from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    При необходимости можно расширять полями (телефон, аватар и т.п.).
    """
    # пример расширения (не обязательно):
    # telegram_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self) -> str:
        return self.username


class TelegramProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="telegram_profile")
    telegram_chat_id = models.CharField(max_length=128, unique=True)

    def __str__(self) -> str:
        return f"{self.user.username}: {self.telegram_chat_id}"