from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Habit
from .services import send_telegram_message


@shared_task
def send_habit_reminders():
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)
    today = now.date()

    # Берём только полезные, не приятные привычки
    habits = Habit.objects.filter(
        is_pleasant=False,
        time=current_time,
    )

    for habit in habits:
        last = habit.last_reminder
        if last is not None:
            days_passed = (today - last).days
            if days_passed < habit.periodicity:
                # Ещё рано напоминать
                continue

        user = habit.owner
        profile = getattr(user, "telegram_profile", None)
        chat_id = getattr(profile, "chat_id", None)
        if not chat_id:
            continue

        text = (
            f"Напоминание о привычке:\n"
            f"{habit.action} в {habit.time.strftime('%H:%M')} "
            f"в месте: {habit.place}"
        )
        send_telegram_message(chat_id, text)

        habit.last_reminder = today
        habit.save(update_fields=["last_reminder"])