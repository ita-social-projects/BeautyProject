"""The module includes serializers for Position model."""

from rest_framework import serializers

from api.models import Position, Business
from api.serializers.serializers_customuser import CustomUserSerializer
from api.serializers.business_serializers import BusinessListCreateSerializer


class PositionSerializer(serializers.ModelSerializer):
    """Custom HyperlinkedRelatedField for user orders."""

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Position
        fields = ['name', 'specialist', 'business', 'start_time', 'end_time']
    