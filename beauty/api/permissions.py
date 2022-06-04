"""Module with permissions for api appliaction."""

import logging

from rest_framework import permissions
from django.contrib.auth.models import Group


logger = logging.getLogger(__name__)


class IsAccountOwnerOrReadOnly(permissions.BasePermission):
    """IsAccountOwnerOrReadOnly permission class.

    Object-level permission to only allow owners of an object
    to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        logger.debug(f"Object {obj.id} permission check")

        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated and (
                request.user.is_admin or (obj == request.user)
            )
        )


class IsAdminOrIsAccountOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission.

    Only allow owners of an object or admin to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        logger.debug(f"Object {obj.id} permission check")

        is_admin = request.user.is_admin
        return request.method in permissions.SAFE_METHODS or is_admin or (obj == request.user)


class IsAdminOrBusinessOwner(permissions.IsAuthenticatedOrReadOnly):
    """IsAdminOrBusinessOwner permission class.

    Object-level permission to only allow owners of an object
    or admin to review and edit it.
    """

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        logger.debug(f"Object {obj.id} permission check")

        if request.user.is_authenticated:
            return request.user.is_admin or (obj == request.user)


class IsOrderUser(permissions.BasePermission):
    """Object-level permission to only allow users of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        logger.debug(f"Object {obj.id} permission check")

        return obj.specialist == request.user or obj.customer == request.user


class IsOwner(permissions.BasePermission):
    """Permission class which checks if current user is an owner."""

    def has_permission(self, request, view):
        """Checks if user belongs to owner group."""
        user = request.user

        if user.is_authenticated:
            try:
                user.groups.get(name="Owner")
                logger.error("User have owner permission")
                return True

            except Group.DoesNotExist:
                logger.error("Current user is not an owner")

        return False


class ReadOnly(permissions.BasePermission):
    """Permission which gives access for SAFE_METHODS."""

    def has_permission(self, request, view):
        """Checks if method in SAFE_METHODS."""
        return request.method in permissions.SAFE_METHODS


class IsPositionOwner(permissions.BasePermission):
    """IsPositionOwner permission class.

    Allows only position owners and specialist to work with it.
    """
    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        logger.debug(f"Object {obj.id} permission check. Is position owner")

        if "Owner" in request.user.groups.all().values_list("name", flat=True):
            return obj.business.owner == request.user
        else:
            return False

