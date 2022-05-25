"""The module includes serializers for Position model."""

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.models import Position
from api.serializers.serializers_customuser import CustomUserSerializer


class PositionSerializer(serializers.HyperlinkedRelatedField):
    """Custom HyperlinkedRelatedField for user orders."""

    url = serializers.HyperlinkedIdentityField(
        view_name='api:position-detail', lookup_field='pk'
    )
    specialist = CustomUserSerializer(many=True, read_only=True)
    # business = BusinessSeializer(read_only=True)

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Position
        fields = ['name', 'start_time', 'end_time']
    