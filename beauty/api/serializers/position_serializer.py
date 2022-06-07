"""The module includes serializers for Position model."""

import logging
from rest_framework import serializers
from api.models import Position


logger = logging.getLogger(__name__)


class PositionSerializer(serializers.ModelSerializer):
    """Custom HyperlinkedRelatedField for user orders."""

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Position
        fields = ["name", "specialist", "business", "start_time", "end_time"]

    def validate(self, data: dict) -> dict:
        """Validate start and end time.

        Args:
            data (dict): dictionary with data for user creation

        Returns:
            data (dict): dictionary with validated data for user creation

        """
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if end_time < start_time:
            logger.info("Postion_serializer: end time should go after start time")
            raise serializers.ValidationError(
                {"end_time": "end time should go after start time"},
            )

        logger.info("Position_serializer: successfully set time")

        return super().validate(data)
