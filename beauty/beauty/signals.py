"""Module with all project signals. """

from django.dispatch import Signal, receiver
from rest_framework.reverse import reverse
from beauty.utils import StatusOrderEmail

order_status_changed = Signal()


@receiver(order_status_changed)
def send_order_status_for_customer(sender, **kwargs):
    """Send an email message to the customer with changed
    order status from a specialist.

    Args:
        sender (OrderApprovingView): class sender
        **kwargs (order, request): kwargs from a sender class
    """
    order = kwargs['order']
    request = kwargs['request']
    context = {"order": order,
               "redirect_url": reverse("api:user-order-detail",
                                       args=[order.customer.id, order.id])}
    StatusOrderEmail(request, context).send([order.customer.email, ])
