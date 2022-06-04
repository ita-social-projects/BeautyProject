"""Module with all project signals."""
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from rest_framework.reverse import reverse

from api.models import Order
from beauty.tokens import OrderApprovingTokenGenerator
from beauty.utils import StatusOrderEmail
import logging


logger = logging.getLogger(__name__)

order_status_changed = Signal()


@receiver(post_save, sender=Order, dispatch_uid="create_token_for_order")
def create_token_for_order(sender, instance, created, **kwargs):
    """Create order token."""
    if created:
        instance.token = OrderApprovingTokenGenerator().make_token(instance)
        instance.save()


@receiver(order_status_changed)
def send_order_status_for_customer(sender, **kwargs):
    """Send order status for the customer.

    Send an email message to the customer with changed
    order status from a specialist.

    Args:
        sender (OrderApprovingView): class sender
        **kwargs (order, request): kwargs from a sender class
    """
    logger.info(f"Signal was received from {sender.__name__}")

    order = kwargs["order"]
    request = kwargs["request"]
    context = {"order": order,
               "redirect_url": reverse("api:user-order-detail",
                                       args=[order.customer.id, order.id])}

    logger.info(f"Email was sent to the {order.customer.get_full_name()} with "
                f"specialist {order.specialist.get_full_name()}"
                f"decision(order was {order.get_status_display()})")

    StatusOrderEmail(request, context).send([order.customer.email])
