from django.conf import settings
from django.db import models


class Habit(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField("Место", max_length=255)
    time = models.TimeField("Время")
    action = models.CharField("Действие", max_length=255)

    is_pleasant = models.BooleanField(
        "Приятная привычка",
        default=False,
        help_text="Если включено — это приятная (вознаграждающая) привычка",
    )

    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reward_for",
        verbose_name="Связанная привычка",
        help_text="Приятная привычка, которая идёт как награда",
    )

    periodicity = models.PositiveSmallIntegerField(
        "Периодичность (в днях)",
        default=1,
        help_text="Как часто выполнять привычку (1–7 дней)",
    )

    reward = models.CharField(
        "Вознаграждение",
        max_length=255,
        null=True,
        blank=True,
        help_text="Текстовое вознаграждение (если не используем приятную привычку)",
    )

    execution_time = models.PositiveSmallIntegerField(
        "Время на выполнение (сек.)",
        default=60,
        help_text="Не больше 120 секунд",
    )

    is_public = models.BooleanField(
        "Публичная привычка",
        default=False,
        help_text="Если включено — привычка видна другим пользователям",
    )

    last_reminder = models.DateField(
        "Дата последнего напоминания",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.owner} — {self.action} в {self.time} ({self.place})"
