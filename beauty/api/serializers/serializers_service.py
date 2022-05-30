"""The module includes serializers for Service model."""
import logging

from rest_framework import serializers
from api.models import Service


logger = logging.getLogger(__name__)


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service fields"""

    name = serializers.CharField(max_length= 50)
    price = serializers.DecimalField(max_digits=5, decimal_places=2)
    description = serializers.CharField(max_length=250)
    duration = serializers.IntegerField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'description', 'duration']

