from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow owners of an object to edit it; read-only for others."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Instance must have an attribute `reporter` or `user` to check
        user = request.user
        if not user or not user.is_authenticated:
            return False
        owner = getattr(obj, 'reporter', None) or getattr(obj, 'user', None)
        return owner == user or user.is_staff


class IsNGO(permissions.BasePermission):
    """Allow access only to users with role 'ngo' or staff."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        try:
            profile = user.profile
            return profile.role == 'ngo' or user.is_staff
        except Exception:
            return False
