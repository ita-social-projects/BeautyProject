"""The module includes serializers for Business model."""

import logging

from rest_framework import serializers

from api.models import Location


logger = logging.getLogger(__name__)


class LocationSerializer(serializers.ModelSerializer):
    """Location serializer."""

    class Meta:
        """Displays address fields."""
        model = Location
        fields = "__all__"
