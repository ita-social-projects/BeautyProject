"""The module includes serializers for Order model."""

from rest_framework import serializers
from api.models import (Order, CustomUser, Service)


class SpecialistRelatedField(serializers.PrimaryKeyRelatedField):
    """RelatedField for choose specialist in the POST method."""

    def get_queryset(self):
        """Get query with all users which are specialists."""
        return self.queryset.filter(
                groups__name__icontains="specialist")


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for getting all orders and creating a new order."""

    url = serializers.HyperlinkedIdentityField(
        view_name='api:order-detail', lookup_field='pk'
    )
    specialist = SpecialistRelatedField(queryset=CustomUser.objects.all())
    customer = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all())
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all())

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Order
        fields = '__all__'
