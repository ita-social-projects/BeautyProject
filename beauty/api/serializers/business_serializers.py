from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from api.models import Business

User = get_user_model()


class BusinessListCreateSerializer(serializers.ModelSerializer):
    """Business serilalizer for list and create views"""

    class Meta:
        """Display 4 required fields for Business creation"""

        model = Business
        fields = ('name', 'type', 'owner', 'description')

    def validate_owner(self, value):
        """Checks if such user exists and validates if user belongs to
        Specialist group
        """
        group = value.groups.filter(name="Owner").first()
        if group is None:
            raise ValidationError(
                _('Only Owners can create Business'), code='invalid'
            )

        return value

    def to_representation(self, instance):
        """Display owner full name"""
        data = super().to_representation(instance)
        owner = User.objects.filter(id=data["owner"]).first()
        data["owner"] = owner.get_full_name()
        return data
