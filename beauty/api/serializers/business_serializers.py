"""The module includes serializers for Business model."""
import logging

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
        fields = ("name", "type", "owner", "description")

    def validate_owner(self, value):
        """User validation.

        Checks if such user exists and validates if user belongs to
        Specialist group
        """
        group = value.groups.filter(name="Owner").first()
        if group is None:
            raise ValidationError(
                _("Only Owners can create Business"), code="invalid",
            )

        return value

    def to_representation(self, instance):
        """Display owner full name."""
        data = super().to_representation(instance)
        owner = CustomUser.objects.filter(id=data["owner"]).first()
        data["owner"] = owner.get_full_name()
        return data


class BusinessesSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for business base fields."""

    name = serializers.CharField(max_length=20)
    type = serializers.CharField(max_length=100) # noqa
    address = serializers.CharField(max_length=500)

    class Meta:
        """Meta for OwnerBusinessesSerializer class."""

        model = Business
        fields = ("name", "type", "address")


class BusinessAllDetailSerializer(serializers.ModelSerializer):
    """Serializer for specific business."""

    owner_name = serializers.SerializerMethodField()
    created_at = serializers.ReadOnlyField()
    address = serializers.CharField(max_length=500)

    def get_owner_name(self, obj):
        """Return full name of business owner."""
        full_name = f"{obj.owner.first_name} {obj.owner.last_name}"
        logger.debug("Owner name transferred to frontend")
        return full_name

    class Meta:
        """Meta for BusinessDetailSerializer class."""

        model = Business
        fields = ("owner_name", "created_at", "logo", "name", "type", "address", "description")


class BusinessDetailSerializer(serializers.ModelSerializer):
    """Serializer for specific business."""

    address = serializers.CharField(max_length=500)

    class Meta:
        """Meta for BusinessDetailSerializer class."""

        model = Business
        fields = ("logo", "name", "type", "address", "description")
