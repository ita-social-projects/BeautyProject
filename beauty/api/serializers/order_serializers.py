"""The module includes serializers for Order model."""

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from api.models import (Order, CustomUser, Service, Position)


class SpecialistRelatedField(serializers.PrimaryKeyRelatedField):

    def get_queryset(self):
        return self.queryset.filter(
            groups__name__icontains="specialist")

    # def get_queryset(self):
    #     queryset = self.queryset
    #     if self.specialist and not self.service and self.filter_field == "specialist":
    #         print()
    #         queryset = self.queryset.filter(
    #             groups__name__icontains=self.filter_field)
    #     elif not self.specialist and self.service:
    #         queryset = self.queryset
    #     elif self.specialist and self.service:
    #             queryset = self.queryset.filter(
    #                 groups__name__icontains=self.filter_field, position__service_id=self.service)
    #     return queryset

    # def to_internal_value(self, data):
    #     obj = super().to_internal_value(data)
    #     if isinstance(obj, CustomUser):
    #         self.specialist = obj.id
    #     elif isinstance(obj, Service):
    #         self.service = obj.id
    #     return obj


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
        service = validated_data.get("service")
        specialist = validated_data.get("specialist")
        specialist_services = Position.objects.filter(
            specialist=specialist).values_list("service__name", flat=True)
        if not service.position.specialist.filter(id=specialist.id):
            raise serializers.ValidationError(
                {"service": "Specialist does not have such service.",
                 "help_text": f"Specialist has such services "
                              f"{list(specialist_services)}."}
            )
        return super().create(validated_data)
