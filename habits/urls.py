from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import HabitViewSet, PublicHabitViewSet

router = DefaultRouter()
router.register("habits", HabitViewSet, basename="habit")
router.register("public-habits", PublicHabitViewSet, basename="public-habit")

urlpatterns = [
    path("", include(router.urls)),
]

