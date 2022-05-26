from rest_framework import serializers
from api.models import Business
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class BusinessListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('name', 'type', 'owner', 'description')

    def validate_owner(self, value):
        """Checks if such user exists and validates if user belongs to
        Specialist group
        """
        user = User.objects.filter(id=value).first()
        if user is None:
            raise ValidationError(_('User does not exist'), code='invalid')

        group = user.groups.filter(group__name="Specialist").exists()
        if not group:
            raise ValidationError(
                _('User must belong to Specialist group'), code='invalid'
            )

        return value

    def to_representation(self, instance):
        """Display owner full name"""
        data = super().to_representation(instance)
        owner = User.objects.filter(id=data["owner"]).first()
        data["owner"] = owner.get_full_name()
        return data
