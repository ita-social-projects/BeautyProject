"""The module includes serializers for Position model."""

import logging
import calendar

from rest_framework import serializers
from beauty.utils import string_to_time
from api.serializers.business_serializers import WorkingTimeSerializer
from api.models import Position, CustomUser

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


def is_inside_interval(main_interval: tuple, inner_interval: tuple):
    """Return True if inner interval is inside main_interval."""
    return (
        inner_interval[0] >= main_interval[0]
    ) and (
        inner_interval[1] <= main_interval[1]
    )


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

    def is_valid(self):
        """Method for validation.

        This method checks whether user exists and validates an email. It also
        checks that user is not assigned to this position already.

        """
        email_to_check = self.initial_data["email"]
        super().is_valid(email_to_check)
        pos_to_check = self.initial_data["position"]
        user = CustomUser.objects.filter(email=email_to_check)
        position = Position.objects.get(pk=pos_to_check)

        if user.exists():
            if user.get() not in position.specialist.all():
                return True
            else:
                raise serializers.ValidationError(
                    detail="User is already on the Position.",
                    code=400,
                )
        return False
