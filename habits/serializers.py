from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("owner", "last_reminder", "created_at", "updated_at")

    def validate(self, attrs):
        is_pleasant = attrs.get(
            "is_pleasant",
            getattr(self.instance, "is_pleasant", False),
        )
        reward = attrs.get("reward", getattr(self.instance, "reward", None))
        related_habit = attrs.get(
            "related_habit",
            getattr(self.instance, "related_habit", None),
        )
        execution_time = attrs.get(
            "execution_time",
            getattr(self.instance, "execution_time", None),
        )
        periodicity = attrs.get(
            "periodicity",
            getattr(self.instance, "periodicity", None),
        )

        # 1. Исключить одновременный выбор связанной привычки и указания вознаграждения.
        if reward and related_habit:
            raise serializers.ValidationError(
                "Нельзя одновременно указывать и вознаграждение, и связанную привычку."
            )

        # 2. Время выполнения не больше 120 секунд.
        if execution_time is not None and execution_time > 120:
            raise serializers.ValidationError(
                "Время выполнения привычки не может превышать 120 секунд."
            )

        # 3. В связанные привычки могут попадать только приятные привычки.
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                "В связанную привычку можно выбирать только привычку с признаком приятной."
            )

        # 4. У приятной привычки не может быть вознаграждения или связанной привычки.
        if is_pleasant:
            if reward or related_habit:
                raise serializers.ValidationError(
                    "У приятной привычки не может быть вознаграждения "
                    "или связанной привычки."
                )

        # 5. Нельзя выполнять привычку реже, чем 1 раз в 7 дней.
        if periodicity is not None and not (1 <= periodicity <= 7):
            raise serializers.ValidationError(
                "Периодичность должна быть от 1 до 7 дней."
            )

        return attrs

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
