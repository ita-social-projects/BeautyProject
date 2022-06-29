"""The module includes serializers for Position model."""

import logging
import calendar

from rest_framework import serializers
from beauty.utils import string_to_time, is_inside_interval
from api.serializers.business_serializers import WorkingTimeSerializer
from api.models import Position


logger = logging.getLogger(__name__)


def is_valid_position_time(business_time, data):
    """Return True if position time within business time."""
    week_days = [day.capitalize() for day in calendar.HTMLCalendar.cssclasses]

    for time in week_days:
        if len(business_time[time]) < len(data[time]):
            return False
        if len(business_time[time]) > len(data[time]):
            continue
        if len(business_time[time]) == len(data[time]) == 0:
            continue

        inner_interval = (
            string_to_time(data[time][0]),
            string_to_time(data[time][1]),
        )

        main_interval = (
            string_to_time(business_time[time][0]),
            string_to_time(business_time[time][1]),
        )

        if not is_inside_interval(main_interval, inner_interval):
            return False
    return True


class PositionGetSerializer(serializers.ModelSerializer):
    """Position serializer for get all position method."""

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Position
        fields = ["name", "specialist", "business", "working_time"]


class PositionSerializer(WorkingTimeSerializer):
    """Position serializer for position creation."""

    class Meta:
        """Class with a model and model fields for serialization."""

        week_days = [day.capitalize()
                     for day in calendar.HTMLCalendar.cssclasses]
        model = Position
        fields = ["name", "specialist", "business", *week_days]

    def validate(self, data: dict) -> dict:
        """Validate start and end time.

        Args:
            data (dict): dictionary with data for user creation

        Returns:
            data (dict): dictionary with validated data for user creation

        """
        business = data.get("business")
        business_time = business.working_time

        if business and business.owner != self.context["request"].user:
            raise serializers.ValidationError(
                {"business": "you aren't business owner"},
            )

        if not is_valid_position_time(business_time, data):
            raise serializers.ValidationError(
                {"working_time": "Position time isn't within working time"},
            )

        logger.info("Position_serializer: successfully set time")

        return super().validate(data)


class PositionInviteSerializer(serializers.Serializer):
    """This is a serializer for inviting new specialists to a Position."""
    email = serializers.EmailField()
