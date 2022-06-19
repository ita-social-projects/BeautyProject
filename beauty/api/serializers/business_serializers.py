"""The module includes serializers for Business model."""

import logging
import re
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
            data (dict): dictionary with data for user creation

        Returns:
            data (dict): dictionary with validated data for user creation

        """
        hours_fields = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        for time in hours_fields:
            if len(data[time]) not in [0, 2]:
                raise serializers.ValidationError(
                    {f"{time}": "Must contain 2 elements or 0."},
                )

            if len(data[time]) == 2:
                if not (
                    re.search(
                        r"^\d{2}:\d{2}$",
                        data[time][0],
                    ) and re.search(
                        r"^\d{2}:\d{2}$",
                        data[time][1],
                    )
                ):
                    raise serializers.ValidationError(
                        {f"{time}":
                         "Doesn't match template like 00:00-00:00."},
                    )

        return super().validate(data)

    def create(self, validated_data: dict):
        """Create a new business using dict with data.

        Args:
            validated_data (dict): validated data for new business creation

        Returns:
            business (object): new business

        """
        hours_fields = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        json_field = {key: value if len(value) != 2 else [
                      datetime.strptime(value[0], "%H:%M").time().__str__(),
                      datetime.strptime(value[1], "%H:%M").time().__str__(),
                      ]
                      for key, value in validated_data.items()
                      if key in hours_fields}

        for key in hours_fields:
            validated_data.pop(key)

        validated_data["working_time"] = json_field
        return super().create(validated_data)


class BusinessCreateSerializer(BaseBusinessSerializer, WorkingTimeSerializer):
    """Business serilalizer for list and create views."""

    class Meta:
        """Display 3 required fields for Business creation."""

        hours_fields = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        model = Business
        fields = ("name", "business_type", "owner", "description",
                  *hours_fields)
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

        model = Business
        fields = ("owner", "name", "business_type", "logo", "owner", "address",
                  "description", "created_at", "working_time")
