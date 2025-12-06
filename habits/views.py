from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination

from .models import Habit
from .permissions import IsOwnerHabit
from .serializers import HabitSerializer


class HabitPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50


class HabitViewSet(viewsets.ModelViewSet):
    """
    CRUD только по своим привычкам.
    """
    serializer_class = HabitSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerHabit)
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)


class PublicHabitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Список публичных привычек (только чтение).
    """
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
