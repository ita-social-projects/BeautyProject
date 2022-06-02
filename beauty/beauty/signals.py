"""Module with all project signals."""

from django.dispatch import Signal, receiver
from rest_framework.reverse import reverse
from beauty.utils import StatusOrderEmail
import logging


logger = logging.getLogger(__name__)

order_status_changed = Signal()


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
