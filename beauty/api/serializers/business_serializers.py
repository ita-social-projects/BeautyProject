"""The module includes serializers for Business model."""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from rest_framework import serializers

from api.models import (Business, CustomUser)


User = get_user_model()
logger = logging.getLogger(__name__)


class BusinessListCreateSerializer(serializers.ModelSerializer):
    """Business serilalizer for list and create views."""

    class Meta:
        """Display 4 required fields for Business creation."""

        model = Business
        fields = ("name", "business_type", "owner", "description")

    def validate_owner(self, value):
        """Validates owner.

        Checks if such user exists, validates if user belongs to
        Specialist group
        """
        try:
            value.groups.get(name="Owner")

        except Group.DoesNotExist:
            logger.error("Failed owner validation")

            raise ValidationError(
                _("Only Owners can create Business"), code="invalid",
            )

        logger.info("Sucessfully validated owner")

        return value

    def to_representation(self, instance):
        """Display owner full name."""
        data = super().to_representation(instance)
        owner = User.objects.filter(id=data["owner"]).first()
        data["owner"] = owner.get_full_name()
        return data


class BusinessesSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for business base fields."""
    business_url = serializers.HyperlinkedIdentityField(
        view_name="api:business-detail", lookup_field="pk",
    )
    owner_url = serializers.HyperlinkedIdentityField(
        view_name="api:certain-owners-businesses-list", lookup_field="owner_id",
    )
    address = serializers.CharField(max_length=500)

    class Meta:
        """Display main field & urls for businesses."""

        model = Business
        fields = ("business_url", "owner_url", "name", "business_type", "address")


class BusinessAllDetailSerializer(serializers.ModelSerializer):
    """Serializer for specific business."""

    created_at = serializers.ReadOnlyField()
    address = serializers.CharField(max_length=500)

    def to_representation(self, instance):
        """Change the display of owner field data."""
        data = super().to_representation(instance)
        owner = CustomUser.objects.get(id=data["owner"])
        data["owner"] = owner.get_full_name()
        return data

    class Meta:
        """Meta for BusinessDetailSerializer class."""

        model = Business
        fields = ("owner", "created_at", "logo", "name", "business_type", "address",
                  "description")


class BusinessDetailSerializer(serializers.ModelSerializer):
    """Serializer for specific business."""

    address = serializers.CharField(max_length=500)

    class Meta:
        """Meta for BusinessDetailSerializer class."""

        model = Business
        fields = ("logo", "name", "business_type", "address", "description")


class BusinessGetAllInfoSerializers(serializers.ModelSerializer):
    """Serializer for getting all info about business."""

    def to_representation(self, instance):
        """Change the display of owner field data."""
        data = super().to_representation(instance)
        owner = CustomUser.objects.get(id=data["owner"])
        data["owner"] = owner.get_full_name()
        return data

    class Meta:
        """Meta for BusinessGetAllInfoSerializers class."""

        model = Business
        fields = ["owner", "name", "business_type", "logo", "owner", "address",
                  "description", "created_at"]
