"""The module includes serializers for Position model."""

import logging
import calendar
from datetime import datetime
from rest_framework import serializers
from api.models import Position

from api.serializers.business_serializers import WorkingTimeSerializer


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
            datetime.strptime(data[time][0], "%H:%M"),
            datetime.strptime(data[time][1], "%H:%M"),
        )
        main_interval = (
            datetime.strptime(business_time[time][0], "%H:%M:%S"),
            datetime.strptime(business_time[time][1], "%H:%M:%S"),
        )

        if not is_inside_interval(main_interval, inner_interval):
            return False
    return True


def is_inside_interval(main_interval: tuple, inner_interval: tuple):
    """Return True if inner interval is inside main_interval."""
    if inner_interval[0] < main_interval[0]:
        return False
    elif inner_interval[1] > main_interval[1]:
        return False
    else:
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
