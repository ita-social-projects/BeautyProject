"""The module includes serializers for Business model."""

import calendar
import logging

from rest_framework import serializers

from beauty.utils import get_working_time_from_dict
from api.models import (Business, CustomUser)


logger = logging.getLogger(__name__)


class WorkingTimeSerializer(serializers.ModelSerializer):
    """Business serilalizer for working hours.

    Provides proper business creation and validation based on set working hours.
    """
    week_days = [day.capitalize() for day in calendar.HTMLCalendar.cssclasses]

    Sun = serializers.ListField(
        write_only=True,
        max_length=2,
        default=[],
    )
    Mon = serializers.ListField(
        write_only=True,
        max_length=2,
        default=[],
    )
    Tue = serializers.ListField(
        write_only=True,
        max_length=2,
        default=[],
    )
    Wed = serializers.ListField(
        write_only=True,
        max_length=2,
        default=[],
    )
    Thu = serializers.ListField(
        write_only=True,
        max_length=2,
        default=[],
    )
    Fri = serializers.ListField(
        write_only=True,
        max_length=2,
        default=[],
    )
    Sat = serializers.ListField(
        write_only=True,
        max_length=2,
        default=[],
    )

    def validate(self, data: dict):
        """Validate working hours.

        Args:
            data (dict): dictionary with data for business creation

        Returns:
            data (dict): dictionary with validated data for business creation

        """
        week_days = [day.capitalize() for day in calendar.HTMLCalendar.cssclasses]
        days_in_data = set(week_days).intersection(set(data.keys()))
        if self.context["request"].method in ["POST", "PUT"]:
            # If missing or invalid name at least in one day in data.keys()
            if len(days_in_data) != 7:
                raise serializers.ValidationError(
                    {"Working_time": "Day name not match main structure or missing."},
                )

        if self.context["request"].method == "PATCH":
            # If no days in PATCH method (empty set)
            if not days_in_data:
                return super().validate(data)

            for day in set(week_days).difference(days_in_data):
                data[day] = self.instance.working_time[day]

        # Time validation, raises serializers.ValidationError if something wrong
        data["working_time"] = get_working_time_from_dict(data)

        return super().validate(data)

    def create(self, validated_data: dict):
        """Create a new business using dict with data.

        Args:
            validated_data (dict): validated data for new business creation

        Returns:
            business (object): new business

        """
        json_field = {key: value if len(value) != 2 else [
                      value[0],
                      value[1],
                      ]
                      for key, value in validated_data.items()
                      if key in self.week_days}

        for key in self.week_days:
            validated_data.pop(key)

        validated_data["working_time"] = json_field
        return super().create(validated_data)


class BaseBusinessSerializer(WorkingTimeSerializer):
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


class BusinessCreateSerializer(BaseBusinessSerializer):
    """Business serializer for list and create views."""

    class Meta:
        """Display required fields for Business creation."""

        week_days = [day.capitalize()
                     for day in calendar.HTMLCalendar.cssclasses]
        model = Business
        fields = ("name", "business_type", "owner", "description", *week_days)
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


class BusinessGetAllInfoSerializers(BaseBusinessSerializer):
    """Serializer for getting all info about business."""

    address = serializers.CharField(max_length=500)

    class Meta:
        """Meta for BusinessGetAllInfoSerializers class."""

        week_days = [day.capitalize()
                     for day in calendar.HTMLCalendar.cssclasses]
        model = Business
        fields = "__all__"
        extra_fields = (*week_days,)
