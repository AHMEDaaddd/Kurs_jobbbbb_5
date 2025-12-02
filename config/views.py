# config/views.py
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({"message": "Habit tracker API is running"})