from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners of an object
    or admin to edit it.
    """

    def has_permission(self, request, view):
        """Read permissions are allowed to any request,
        so we'll always allow GET, HEAD or OPTIONS requests.
        """
        return bool(request.method in permissions.SAFE_METHODS)


class IsAdminOrIsAccountOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners of an object
    or admin to edit it.
    """

    def has_permission(self, request, view):
        """Read permissions are allowed to any request,
        so we'll always allow GET, HEAD or OPTIONS requests.
        """
        return bool(request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user.is_admin or (obj.email == request.user.email):
                return True
        return False


class IsAccountOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def has_permission(self, request, view):
        """Read permissions are allowed to any request,
        so we'll always allow GET, HEAD or OPTIONS requests.
        """
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(obj.email == request.user.emai)
