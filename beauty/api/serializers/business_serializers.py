"""The module includes serializers for Business model."""

import calendar
import logging

from rest_framework import serializers

from beauty.utils import Geolocator, string_to_time, time_to_string
from api.models import (Business, CustomUser, Location)
from api.serializers.location_serializer import LocationSerializer


logger = logging.getLogger(__name__)


class BaseBusinessSerializer(serializers.ModelSerializer):
    """Base business serilalizer.

    Provides to_representation which display owner with his full_name
    """
    location = LocationSerializer()

    def correct_coordinates(self, address: str, latitude=None, longitude=None):
        """Correct invalid coordinates."""
        if not ((0 < latitude < 180) and (0 < longitude < 180)):
            return Geolocator().get_coordinates_by_address(address)

        return latitude, longitude

    def create(self, validated_data):
        """Overridden to create the nested Location model.

        In case when only address of location is provided, or one of coordinates is missed
        location coordinates are calculated by address field.
        """
        location = self.initial_data["location"]

        try:
            location["latitude"], location["longitude"] = self.correct_coordinates(**location)
            location_model = Location.objects.create(**location)
            validated_data["location"] = location_model

            return super().create(validated_data)

        except TypeError:
            logger.warning(f"Cannot update address {location}")
            raise serializers.ValidationError({"location": "Invalid location details provided"})

    def update(self, instance, validated_data):
        """Overridden to update the nested Location model.

        In case when only address of location is provided, or one of coordinates is missed
        location coordinates are calculated by address field.
        """
        location_serializer = self.fields["location"]
        location_instance = instance.location
        location = validated_data.pop("location")
        location_data = dict(location)

        try:
            location["latitude"], location["longitude"] = self.correct_coordinates(**location_data)
            location_serializer.update(location_instance, location)
            return super().update(instance, validated_data)

        except TypeError:
            logger.warning(f"Cannot update address {location}")
            raise serializers.ValidationError({"location": "Invalid location details provided"})

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
        working_time = {day: [] for day in self.week_days}
        for day in self.week_days:

            if day not in data.keys():
                raise serializers.ValidationError(
                    {day: "Day name not match main structure or missing."},
                )

            amount_of_data = len(data[day])
            if amount_of_data not in [0, 2]:
                raise serializers.ValidationError(
                    {day: "Must contain 2 elements or 0."},
                )

            if amount_of_data == 2:

                try:
                    opening_time = string_to_time(data[day][0])
                    closing_time = string_to_time(data[day][1])
                    working_time[day].append(time_to_string(opening_time))
                    working_time[day].append(time_to_string(closing_time))
                except ValueError:
                    raise serializers.ValidationError(
                        {day: "Day schedule does not match the template\
                              ['HH:MM', 'HH:MM']."},
                    )

                if opening_time > closing_time:

                    raise serializers.ValidationError(
                        {day:
                            "working hours must begin before they end."},
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
                      value[0],
                      value[1],
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
    location = LocationSerializer()

    class Meta:
        """Display main field & urls for businesses."""

        model = Business
        fields = (
            "business_url", "name", "business_type", "working_time", "location",
        )


class BusinessDetailSerializer(BaseBusinessSerializer):
    """Serializer for specific business."""

    class Meta:
        """Meta for BusinessDetailSerializer class."""

        model = Business
        exclude = ("created_at", "id", "owner", "is_active")


class BusinessGetAllInfoSerializers(BaseBusinessSerializer):
    """Serializer for getting all info about business."""

    class Meta:
        """Meta for BusinessGetAllInfoSerializers class."""

        model = Business
        fields = "__all__"
