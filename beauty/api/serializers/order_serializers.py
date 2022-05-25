"""The module includes serializers for Order model."""

from rest_framework import serializers
from api.models import Order


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for getting all orders and creating a new order."""

    url = serializers.HyperlinkedIdentityField(
        view_name='api:order-detail', lookup_field='pk'
    )
    specialist = serializers.PrimaryKeyRelatedField(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    service = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Order
        fields = '__all__'
