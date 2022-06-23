"""The module includes serializers for Order model."""

from rest_framework.exceptions import ValidationError
from django.utils import timezone
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

    def validate(self, attrs):
        """Validate data.

        Args:
            attrs: data from fields

        Returns: validated data
        """
        request = self.context.get("request")
        specialist = attrs.get("specialist")
        start_time = attrs.get("start_time")
        service = attrs.get("service")

        errors = {}
        if timezone.now() > start_time:
            logger.info("The start time should be later than now.")

            errors.update({"start_time": "The start time should be later than now."})
        specialist_services = Position.objects.filter(
            specialist=specialist).values_list("service__name", flat=True)
        if not service.position.specialist.filter(id=specialist.id):
            logger.info(f"Specialist {specialist.get_full_name()}"
                        f"does not have {service.name} service")

            errors.update(
                {"service": {"message": f"Specialist {specialist.get_full_name()} does not have "
                                        f"{service.name} service.",
                             "help_text": f"Specialist {specialist.get_full_name()} "
                                          f"has such services {list(specialist_services)}."}},
            )
        if specialist == request.user:
            logger.info("Customer and specialist are the same person!")

            errors.update({"users": "Customer and specialist are the same person!"})
        if errors:
            raise ValidationError(errors)
        return super().validate(attrs)


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
