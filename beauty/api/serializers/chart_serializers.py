"""Module with serialiers for charts."""

from rest_framework import serializers


class ChartSerializer(serializers.Serializer):
    """Serializer for Chart class."""
    labels = serializers.ListField(child=serializers.CharField(max_length=12))
    data = serializers.ListField(child=serializers.IntegerField(min_value=0))
