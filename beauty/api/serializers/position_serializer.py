"""The module includes serializers for Position model."""

import logging
from datetime import datetime
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

        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        if isinstance(end_time, str):
            start_time = datetime.strptime(start_time, "%H:%M:%S").time()

        if self.instance:
            if start_time and start_time >= self.instance.end_time:
                raise serializers.ValidationError(
                    {"start_time": "end time should go after start time"},
                )
            if end_time and end_time <= self.instance.start_time:
                raise serializers.ValidationError(
                    {"end_time": "end time should go after start time"},
                )

        # If end time is bigger then start time of position
        if start_time and end_time:
            if end_time <= start_time:
                logger.info("Postion_serializer: end time should go after start time")
                raise serializers.ValidationError(
                    {"end_time": "end time should go after start time"},
                )

        logger.info("Position_serializer: successfully set time")

        return super().validate(data)
