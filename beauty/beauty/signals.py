from django.dispatch import Signal, receiver
from django.core.mail import send_mail
from django.template import loader
from rest_framework.reverse import reverse

from beauty.utils import StatusOrderEmail

order_status_changed = Signal()


@receiver(order_status_changed)
def send_order_status_for_customer(sender, **kwargs):
    order = kwargs['order']
    request = kwargs['request']
    context = {"order": order,
               "redirect_url": reverse("api:user-order-detail",
                                       args=[order.customer.id, order.id])}
    StatusOrderEmail(request, context).send([order.customer.email, ])
