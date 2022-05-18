from rest_framework import permissions


class IsOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners of an object
    or admin to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Read permissions are allowed to any request,
        so we'll always allow GET, HEAD or OPTIONS requests.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return False


class IsAdminOrIsAccountOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners of an object
    or admin to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Read permissions are allowed to any request,
        so we'll always allow GET, HEAD or OPTIONS requests.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            if request.user.is_admin or (obj.email == request.user.email):
                return True
        return False


class IsAccountOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        """Read permissions are allowed to any request,
        so we'll always allow GET, HEAD or OPTIONS requests.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated and (obj.email == request.user.email):
            return True
        return False
