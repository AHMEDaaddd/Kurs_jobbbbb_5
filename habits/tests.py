from datetime import time

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient

from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.tasks import send_habit_reminders
from users.models import TelegramProfile


User = get_user_model()


class HabitSerializerValidatorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            password="pass12345",
        )

    def test_cannot_have_reward_and_related_habit(self):
        pleasant = Habit.objects.create(
            owner=self.user,
            place="Дом",
            time=time(10, 0),
            action="Принять ванну",
            is_pleasant=True,
            periodicity=1,
            execution_time=60,
        )

        data = {
            "place": "Улица",
            "time": "09:00:00",
            "action": "Гулять",
            "is_pleasant": False,
            "related_habit": pleasant.id,
            "reward": "Купить кофе",
            "periodicity": 1,
            "execution_time": 60,
        }
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "Нельзя одновременно указывать и вознаграждение",
            str(serializer.errors),
        )

    def test_execution_time_cannot_exceed_120(self):
        data = {
            "place": "Улица",
            "time": "09:00:00",
            "action": "Гулять",
            "is_pleasant": False,
            "periodicity": 1,
            "execution_time": 130,
        }
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "Время выполнения привычки не может превышать 120 секунд",
            str(serializer.errors),
        )

    def test_related_habit_must_be_pleasant(self):
        not_pleasant = Habit.objects.create(
            owner=self.user,
            place="Дом",
            time=time(10, 0),
            action="Работать",
            is_pleasant=False,
            periodicity=1,
            execution_time=60,
        )

        data = {
            "place": "Улица",
            "time": "09:00:00",
            "action": "Гулять",
            "is_pleasant": False,
            "related_habit": not_pleasant.id,
            "periodicity": 1,
            "execution_time": 60,
        }
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "В связанную привычку можно выбирать только привычку с признаком приятной",
            str(serializer.errors),
        )

    def test_pleasant_habit_cannot_have_reward_or_related(self):
        data = {
            "place": "Дом",
            "time": "21:00:00",
            "action": "Играть в приставку",
            "is_pleasant": True,
            "reward": "Купить пиццу",
            "periodicity": 1,
            "execution_time": 60,
        }
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "У приятной привычки не может быть вознаграждения",
            str(serializer.errors),
        )

    def test_periodicity_must_be_between_1_and_7(self):
        data = {
            "place": "Дом",
            "time": "21:00:00",
            "action": "Читать",
            "is_pleasant": False,
            "periodicity": 10,
            "execution_time": 60,
        }
        serializer = HabitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "Периодичность должна быть от 1 до 7 дней",
            str(serializer.errors),
        )


class HabitAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1",
            password="pass12345",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="pass12345",
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_user_sees_only_own_habits(self):
        Habit.objects.create(
            owner=self.user1,
            place="Дом",
            time=time(8, 0),
            action="Зарядка",
            is_pleasant=False,
            periodicity=1,
            execution_time=60,
        )
        Habit.objects.create(
            owner=self.user2,
            place="Офис",
            time=time(9, 0),
            action="Кофе-брейк",
            is_pleasant=False,
            periodicity=1,
            execution_time=60,
        )

        self.authenticate(self.user1)
        url = reverse("habit-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["owner"], self.user1.id)

    def test_user_cannot_edit_foreign_habit(self):
        habit = Habit.objects.create(
            owner=self.user1,
            place="Дом",
            time=time(8, 0),
            action="Зарядка",
            is_pleasant=False,
            periodicity=1,
            execution_time=60,
        )
        self.authenticate(self.user2)
        url = reverse("habit-detail", args=[habit.id])
        response = self.client.patch(url, {"action": "Новая привычка"}, format="json")
        # Объект не попадает в queryset, поэтому 404
        self.assertEqual(response.status_code, 404)

    def test_public_habits_list_available_without_auth(self):
        Habit.objects.create(
            owner=self.user1,
            place="Парк",
            time=time(18, 0),
            action="Гулять",
            is_pleasant=False,
            is_public=True,
            periodicity=1,
            execution_time=60,
        )
        self.client.force_authenticate(user=None)
        url = reverse("public-habit-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_pagination_returns_five_per_page(self):
        for i in range(7):
            Habit.objects.create(
                owner=self.user1,
                place=f"Место {i}",
                time=time(10, 0),
                action=f"Действие {i}",
                is_pleasant=False,
                periodicity=1,
                execution_time=60,
            )

        self.authenticate(self.user1)
        url = reverse("habit-list")
        response = self.client.get(url, {"page": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)

        response_page2 = self.client.get(url, {"page": 2})
        self.assertEqual(response_page2.status_code, 200)
        self.assertEqual(len(response_page2.data["results"]), 2)


class CeleryReminderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            password="pass12345",
        )
        self.profile = TelegramProfile.objects.create(
            user=self.user,
            chat_id="123456789",
        )

    def test_send_habit_reminders_sends_message(self):
        now = timezone.localtime()
        reminder_time = now.time().replace(second=0, microsecond=0)

        Habit.objects.create(
            owner=self.user,
            place="Парк",
            time=reminder_time,
            action="Гулять",
            is_pleasant=False,
            periodicity=1,
            execution_time=60,
        )

        # Мокаем отправку в Telegram
        from unittest.mock import patch

        with patch("habits.tasks.send_telegram_message") as mocked_send:
            send_habit_reminders()
            self.assertTrue(mocked_send.called)
            args, kwargs = mocked_send.call_args
            self.assertEqual(args[0], self.profile.chat_id)