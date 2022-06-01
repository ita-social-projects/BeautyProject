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
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        """Object permission check."""
        logger.debug(f"Object {obj.id} permission check")

        if request.user.is_authenticated:
            return request.user.is_admin or (obj == request.user)


class IsAdminOrIsAccountOwnerOrReadOnly(permissions.BasePermission):
    """IsAdminOrAccountOwnerOrReadOnly permission class.

    Object-level permission to only allow owners of an object
    or admin to edit it.
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
