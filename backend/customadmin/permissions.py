from rest_framework.permissions import BasePermission

class IsAdminUserCustom(BasePermission):
    """
    Allows access only to users marked as custom admins.
    """

    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and getattr(user, 'is_custom_admin', False)