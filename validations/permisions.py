from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    The user is an admin, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or (request.user and request.user.is_staff))
