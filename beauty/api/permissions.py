"""This module provides all needed permissions."""
import logging

from rest_framework import permissions


logger = logging.getLogger(__name__)


class IsAccountOwnerOrReadOnly(permissions.BasePermission):
    """IsAccountOwnerOrReadOnly permission class.

    Object-level permission to only allow owners of an object
    to edit it.
    """

    def has_permission(self, request, view):
        """Read permission.

        Read permissions are allowed to any request,
        so we'll always allow GET, HEAD or OPTIONS requests.
        """
        return bool(request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        logger.debug(f"Object {obj.id} permission check")

        if request.user.is_authenticated:
            if request.user.is_admin or (obj.email == request.user.email):
                return True


class IsAdminOrAccountOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """IsAdminOrAccountOwnerOrReadOnly permission class.

    Object-level permission to only allow owners of an object
    or admin to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        logger.debug(f"Object {obj.id} permission check")

        is_admin = request.user.is_admin
        return bool(request.method in permissions.SAFE_METHODS or is_admin or (obj == request.user))


class IsAdminOrBusinessOwner(permissions.IsAuthenticatedOrReadOnly):
    """IsAdminOrBusinessOwner permission class.

    Object-level permission to only allow owners of an object
    or admin to review and edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        logger.debug(f"Object {obj.id} permission check")

        try:
            is_admin = request.user.is_admin
            return bool(is_admin or (obj == request.user))
        except AttributeError:
            logger.warning(f"User {request.user} has no permission to visit this page")
            raise PermissionError("Cannot obtain object")
