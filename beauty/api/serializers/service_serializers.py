"""The module includes serializers for Service model."""

import logging

from rest_framework import serializers
from api.models import Service

logger = logging.getLogger(__name__)


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service fields."""

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Service
        fields = ["position", "name", "price", "description", "duration"]
