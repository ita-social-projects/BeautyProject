"""The module includes serializers for Business model."""

import logging

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from rest_framework import serializers

from api.models import Business, CustomUser


logger = logging.getLogger(__name__)


class BusinessListCreateSerializer(serializers.ModelSerializer):
    """Serializer for business creation."""

    class Meta:
        """Meta for BusinessListCreateSerializer class."""

        model = Business
        fields = ("name", "business_type", "owner", "description")

    def validate_owner(self, value):
        """User validation.

        Checks if such user exists and validates if user belongs to
        Specialist group
        """
        try:
            value.groups.get(name="Owner")

        except Group.DoesNotExist:
            logger.error("Owner validation failed")
            raise ValidationError(_("Only Owners can create Business"), code="invalid")

        logger.info("Owner was validated")

        return value

    def to_representation(self, instance):
        """Change the display of owner field data."""
        data = super().to_representation(instance)
        owner = CustomUser.objects.get(id=data["owner"])
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
        """Meta for OwnerBusinessesSerializer class."""

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
