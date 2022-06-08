"""The module includes serializers for Business model."""

import logging
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


class BusinessCreateSerializer(BaseBusinessSerializer):
    """Business serilalizer for list and create views."""

    class Meta:
        """Display 3 required fields for Business creation."""

        model = Business
        fields = ("name", "business_type", "owner", "description")
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
        )


class BusinessDetailSerializer(BaseBusinessSerializer):
    """Serializer for specific business."""

    address = serializers.CharField(max_length=500)

    class Meta:
        """Meta for BusinessDetailSerializer class."""

        model = Business
        exclude = ("created_at", "id", "owner")


class BusinessGetAllInfoSerializers(BaseBusinessSerializer):
    """Serializer for getting all info about business."""

    address = serializers.CharField(max_length=500)

    class Meta:
        """Meta for BusinessGetAllInfoSerializers class."""

        model = Business
        fields = ("owner", "name", "business_type", "logo", "owner", "address",
                  "description", "created_at")
