"""The module includes serializers for Business model."""

import calendar
import logging
from datetime import datetime

from rest_framework import serializers

from api.models import (Business, CustomUser)


logger = logging.getLogger(__name__)


class BaseBusinessSerializer(serializers.ModelSerializer):
    """Base business serilalizer.

    Provides to_representation which display owner with his full_name
    """

    def to_representation(self, instance):
        """Display owner full name."""
        data = super().to_representation(instance)
        if "owner" in data:
            owner = CustomUser.objects.get(id=data["owner"])
            data["owner"] = owner.get_full_name()
        return data


class WorkingTimeSerializer(serializers.ModelSerializer):
    """Business serilalizer for working hours.

    Provides proper business creation and validation based on set working hours.
    """
    week_days = [day.capitalize() for day in calendar.HTMLCalendar.cssclasses]

    Sun = serializers.ListField(
        write_only=True,
        required=True,
        max_length=2,
    )
    Mon = serializers.ListField(
        write_only=True,
        required=True,
        max_length=2,
    )
    Tue = serializers.ListField(
        write_only=True,
        required=True,
        max_length=2,
    )
    Wed = serializers.ListField(
        write_only=True,
        required=True,
        max_length=2,
    )
    Thu = serializers.ListField(
        write_only=True,
        required=True,
        max_length=2,
    )
    Fri = serializers.ListField(
        write_only=True,
        required=True,
        max_length=2,
    )
    Sat = serializers.ListField(
        write_only=True,
        required=True,
        max_length=2,
    )

    def validate(self, data: dict):
        """Validate working hours.

        Args:
            data (dict): dictionary with data for business creation

        Returns:
            data (dict): dictionary with validated data for business creation

        """
        working_time = data["working_time"]
        for day in self.week_days:

            amount_of_data = len(working_time[day])
            if amount_of_data not in [0, 2]:
                raise serializers.ValidationError(
                    {f"{day}": "Must contain 2 elements or 0."},
                )

            if len(working_time[day]) == 2:

                try:
                    opening_time = datetime.strptime(working_time[day][0], "%H:%M")
                    closing_time = datetime.strptime(working_time[day][1], "%H:%M")
                    print(type(opening_time), closing_time)

                except ValueError:
                    raise serializers.ValidationError(
                        {f"{day}": f"{day} -day`s schedule does not match the template "
                                   f"['HH:MM', 'HH:MM']."},
                    )

                if opening_time > closing_time:

                    raise serializers.ValidationError(
                        {f"{day}": f"{day} -day working hours must begin before they end."},
                    )

                if opening_time == closing_time:
                    working_time[day] = []

        data["working_time"] = working_time

        return super().validate(data)

    def create(self, validated_data: dict):
        """Create a new business using dict with data.

        Args:
            validated_data (dict): validated data for new business creation

        Returns:
            business (object): new business

        """
        json_field = {key: value if len(value) != 2 else [
                      datetime.strptime(value[0], "%H:%M").time().__str__(),
                      datetime.strptime(value[1], "%H:%M").time().__str__(),
                      ]
                      for key, value in validated_data.items()
                      if key in self.week_days}

        for key in self.week_days:
            validated_data.pop(key)

        validated_data["working_time"] = json_field
        return super().create(validated_data)


class BusinessCreateSerializer(BaseBusinessSerializer, WorkingTimeSerializer):
    """Business serializer for list and create views."""

    class Meta:
        """Display required fields for Business creation."""

        model = Business
        fields = ("name", "business_type", "owner", "description", "working_time")
        read_only_fields = ("owner", )


class BusinessesSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for business base fields."""

    business_url = serializers.HyperlinkedIdentityField(
        view_name="api:business-detail", lookup_field="pk",
    )
    address = serializers.CharField(max_length=500)

    class Meta:
        """Display main field & urls for businesses."""

        model = Business
        fields = (
            "business_url", "name", "business_type", "address",
            "working_time",
        )


class BusinessDetailSerializer(BaseBusinessSerializer):
    """Serializer for specific business."""

    address = serializers.CharField(max_length=500)

    class Meta:
        """Meta for BusinessDetailSerializer class."""

        model = Business
        exclude = ("created_at", "id", "owner", "working_time")


class BusinessGetAllInfoSerializers(BaseBusinessSerializer, WorkingTimeSerializer):
    """Serializer for getting all info about business."""

    address = serializers.CharField(max_length=500)

    class Meta:
        """Meta for BusinessGetAllInfoSerializers class."""

        model = Business
        fields = ("owner", "name", "business_type", "logo", "owner", "address",
                  "description", "created_at", "working_time")
