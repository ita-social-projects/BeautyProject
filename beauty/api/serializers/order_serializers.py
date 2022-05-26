"""The module includes serializers for Order model."""

from rest_framework import serializers
from api.models import (Order, CustomUser, Service, Position)


class SpecialistRelatedField(serializers.PrimaryKeyRelatedField):
    """Custom PrimaryKeyRelatedField for specialist users."""

    def get_queryset(self):
        """Get all specialists."""
        return self.queryset.filter(
            groups__name__icontains="specialist")
