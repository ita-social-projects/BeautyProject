"""Module with permissions for api appliaction"""

from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    """Object-level permission.

    Only allow owners of an object or admin to edit it.
    """

    def has_permission(self, request, view):
        """Read permissions are allowed to any request.

        We'll always allow GET, HEAD or OPTIONS requests.
        """
        return request.method in permissions.SAFE_METHODS


class IsAdminOrIsAccountOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission.

    Only allow owners of an object or admin to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.method in permissions.SAFE_METHODS or
                    request.user.is_admin or (obj == request.user))


class IsAccountOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def has_permission(self, request, view):
        """Read permissions are allowed to any request,
        so we'll always allow GET, HEAD or OPTIONS requests.
        """
        return (
            request.method in permissions.SAFE_METHODS or 
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.email == request.user.emai


class IsOrderUserOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow users of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        return obj.specialist == request.user or obj.customer == request.user
