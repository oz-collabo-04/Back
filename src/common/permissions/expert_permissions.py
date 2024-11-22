from rest_framework.permissions import BasePermission


class IsExpert(BasePermission):
    """
    Allows access only to expert users.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_expert and hasattr(request.user, 'expert'))