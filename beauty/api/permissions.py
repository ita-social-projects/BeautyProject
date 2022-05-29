"""This module provides all needed permissions."""
from rest_framework import permissions


class IsAccountOwnerOrReadOnly(permissions.BasePermission):
    """IsAccountOwnerOrReadOnly permission class.

    Object-level permission to only allow owners of an object
    to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        return bool(request.method in permissions.SAFE_METHODS or
                    obj == request.user)


class IsAdminOrAccountOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """IsAdminOrAccountOwnerOrReadOnly permission class.

    Object-level permission to only allow owners of an object
    or admin to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        return bool(request.method in permissions.SAFE_METHODS or
                    request.user.is_admin or (obj == request.user))


class IsAdminOrBusinessOwner(permissions.IsAuthenticatedOrReadOnly):
    """IsAdminOrBusinessOwner permission class.

    Object-level permission to only allow owners of an object
    or admin to review and edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        try:
            is_admin = request.user.is_admin
            return bool(is_admin or (obj == request.user))
        except AttributeError:
            raise NotImplementedError({"code 404": 'not yet implemented content'})
