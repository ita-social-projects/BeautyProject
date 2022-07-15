"""The module includes serializers for Business model."""

import calendar
import logging

from rest_framework import serializers

from beauty.utils import (Geolocator,
                          get_working_time_from_dict)

from api.models import (Business, CustomUser, Location)
from api.serializers.location_serializer import LocationSerializer


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
        try:
            location = self.initial_data["location"]
            location["latitude"], location["longitude"] = self.correct_coordinates(**location)
            location_model = Location.objects.create(**location)
            validated_data["location"] = location_model

            return super().create(validated_data)

        except KeyError:
            logger.warning("Can not update the address. No address provided")
            raise serializers.ValidationError({"location": "No address provided"})

        except TypeError:
            logger.warning("Can not update the address. The address is in the wrong format")
            raise serializers.ValidationError({"location": "The address is in the wrong format"})

    def update(self, instance, validated_data):
        """Overridden to update the nested Location model.

        In case when only address of location is provided, or one of coordinates is missed
        location coordinates are calculated by address field.
        """
        if self.context["request"].method == "PATCH" and "location" not in validated_data.keys():
            return super().update(instance, validated_data)

        location_serializer = self.fields["location"]
        location_instance = instance.location

        try:
            location = validated_data.pop("location")
            location_data = dict(location)
            location["latitude"], location["longitude"] = self.correct_coordinates(**location_data)
            location_serializer.update(location_instance, location)
            return super().update(instance, validated_data)

        except KeyError:
            logger.warning("Can not update the address. The address is not specified")
            raise serializers.ValidationError({"location": "The address is not specified"})

        except TypeError:
            logger.warning("Can not update the address. The address is in the wrong format")
            raise serializers.ValidationError({"location": "The address is in the wrong format"})

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
    location = LocationSerializer()

    class Meta:
        """Display main field & urls for businesses."""

        model = Business
        fields = (
            "id", "business_url", "name", "business_type", "working_time", "location", "logo"
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

        week_days = [day.capitalize()
                     for day in calendar.HTMLCalendar.cssclasses]
        model = Business
        extra_fields = (*week_days,)
        fields = "__all__"


class BusinessInfoSerializer(serializers.ModelSerializer):
    """Serializer for business base fields."""

    location = LocationSerializer()

    class Meta:
        """Display neccesary field of businesses."""

        model = Business
        fields = ("id", "name", "business_type", "logo", "location", "description", "working_time")


class NearestBusinessesSerializer(BaseBusinessSerializer):
    """Serializer for getting nearest busineses info."""

    business_url = serializers.HyperlinkedIdentityField(
        view_name="api:business-detail", lookup_field="pk",
    )
    location = LocationSerializer()

    class Meta:
        """Meta for NearestBusinessesSerializer class."""

        model = Business
        fields = ("id", "name", "business_type", "business_url", "location")


class AllBusinessesSpecialOwnerSerializer(BaseBusinessSerializer):
    """Serializer for getting all businesses for current owner."""

    location = LocationSerializer()

    class Meta:
        """Display necessary field of businesses."""

        model = Business
        fields = ("id", "name", "business_type", "logo", "location")
