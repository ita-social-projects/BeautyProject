"""."""

from rest_framework import serializers


class LineChartSerializer(serializers.Serializer):
    """."""
    labels = serializers.ListField(child=serializers.CharField(max_length=12))
    data = serializers.ListField(child=serializers.IntegerField(min_value=0))
