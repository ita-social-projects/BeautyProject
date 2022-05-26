"""The module includes serializers for Order model."""

from rest_framework import serializers
from api.models import (Order, CustomUser, Service, Position)


class SpecialistRelatedField(serializers.PrimaryKeyRelatedField):
    """Custom PrimaryKeyRelatedField for specialist users."""

    def get_queryset(self):
        """Get all specialists."""
        return self.queryset.filter(
            groups__name__icontains="specialist")


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for getting all orders and creating a new order."""

    url = serializers.HyperlinkedIdentityField(
        view_name='api:order-detail', lookup_field='pk'
    )
    specialist = SpecialistRelatedField(queryset=CustomUser.objects.all())
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all())

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Order
        fields = '__all__'

    def create(self, validated_data):
        """Check that specialist has the chosen service
         before creating an order.
         """
        service = validated_data.get("service")
        specialist = validated_data.get("specialist")
        specialist_services = Position.objects.filter(
            specialist=specialist).values_list("service__id", flat=True)
        if not service.position.specialist.filter(id=specialist.id):
            raise serializers.ValidationError(
                {"service": "Specialist does not have such service.",
                 "help_text": f"Specialist has such services "
                              f"{list(specialist_services)}."}
            )
        return super().create(validated_data)
