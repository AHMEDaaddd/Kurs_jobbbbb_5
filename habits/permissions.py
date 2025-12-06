from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerHabit(BasePermission):
    """
    Доступ на изменение/удаление — только владельцу.
    Для списка/создания — стандартные IsAuthenticated.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            # читать можно только свои объекты через личное API
            return obj.owner == request.user
        return obj.owner == request.user
