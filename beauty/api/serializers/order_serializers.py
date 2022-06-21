"""The module includes serializers for Order model."""

from rest_framework import serializers
from api.models import (Order, CustomUser, Service, Position)
import logging


logger = logging.getLogger(__name__)


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for getting all orders and creating a new order."""

    url = serializers.HyperlinkedIdentityField(
        view_name="api:order-detail", lookup_field="pk",
    )
    specialist = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        groups__name__icontains="specialist"),
    )
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
    )

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Order
        fields = "__all__"

        read_only_fields = ("customer", "status", "reason")

    def create(self, validated_data):
        """Create.

        Check that specialist has the chosen service
        before creating an order.
        """
        service = validated_data.get("service")
        specialist = validated_data.get("specialist")
        customer = validated_data.get("customer")
        specialist_services = Position.objects.filter(
            specialist=specialist).values_list("service__name", flat=True)
        if not service.position.specialist.filter(id=specialist.id):
            logger.info(f"Specialist {specialist.get_full_name()}"
                        f"does not have {service.name} service")

            raise serializers.ValidationError(
                {"service": f"Specialist {specialist.get_full_name()} does not have "
                            f"{service.name} service.",
                 "help_text": f"Specialist {specialist.get_full_name()} has such services "
                              f"{list(specialist_services)}."},
            )

        if specialist == customer:
            logger.info("Customer and specialist are the same person!")

            raise serializers.ValidationError(
                {"users": "Customer and specialist are the same person!"})
        return super().create(validated_data)


class OrderDeleteSerializer(serializers.ModelSerializer):
    """Serializer for order cancellation."""

    reason = serializers.CharField(required=True)

    class Meta:
        """Class with a model and model fields for serialization."""

        model = Order
        fields = "__all__"
        read_only_fields = ("customer", "start_time",
                            "specialist", "service", "status", "note")

    def update(self, instance: object, validated_data: dict) -> object:
        """Set canceled status for order.

        Args:
            instance (object): instance for changing
            validated_data (dict): validated data for updating instance

        Returns:
            user (object): instance with updated data

        """
        status = Order.StatusChoices
        doesnt_require_decline_list = (status.COMPLETED, status.CANCELLED, status.DECLINED)
        if instance.status in doesnt_require_decline_list:

            logger.info(f"{instance} already has status {instance.get_status_display()}")

            raise serializers.ValidationError(
                {"order": f"Order already has status {instance.get_status_display()}"})

        validated_data["status"] = status.CANCELLED

        logger.info(f"{instance} was canceled")

        return super().update(instance, validated_data)
