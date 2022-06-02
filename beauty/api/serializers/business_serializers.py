"""Module which contains serializers for Business model."""

from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

import logging

from api.models import Business


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

        except User.DoesNotExist:
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
