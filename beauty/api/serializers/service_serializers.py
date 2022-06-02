"""The module includes serializers for Service model."""

from rest_framework import serializers
from api.models import Service

import logging

logger = logging.getLogger(__name__)


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service fields."""

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Service
        fields = ["id", "name", "price", "description", "duration"]
