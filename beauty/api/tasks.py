"""Module with a celery tasks."""

import logging
import smtplib
from beauty.celery import app
from functools import wraps
from api.models import Order
from beauty.utils import (AutoDeclineOrderEmail, RemindAboutOrderEmail, ApprovingOrderEmail)


logger = logging.getLogger(__name__)


def try_except(func):
    """Return a decorator that checks function.

    Args:
        func (function): task function

    Return:
        inner (function): wrapped function
    """
    @wraps(func)
    def inner(*args, **kwargs):
        """Wrapper for task functions with try-except block.

        Args:
            *args: func position arguments
            **kwargs: func keyword arguments
        """
        try:
            func(*args, **kwargs)
        except Order.DoesNotExist:
            logger.info(f"Order with id={args[1]} does not exist")
        except smtplib.SMTPException as ex:
            logger.info(f"SMTPException: {ex.args[0]}")
            args[0].retry(exc=ex, countdown=5)
        except Exception as ex:
            logger.info(f"Error: {ex.args[0]}")
            args[0].retry(exc=ex, countdown=5)
    return inner


@app.task(bind=True, default_retry_delay=5 * 60)
@try_except
def change_order_status_to_decline(self, order_id, site_name):
    """Change new order status to the declined.

     If a specialist did not approve or decline an order during 3 hours it declines automatic.

    Args:
        self: current object
        order_id: order id
        site_name: site URL
    """
    order = Order.objects.get(id=order_id)
    if order.status == Order.StatusChoices.ACTIVE:
        order.status = Order.StatusChoices.DECLINED
        order.save()
        context = {"order": order, "site_name": site_name}

        AutoDeclineOrderEmail(context=context).send([order.customer.email,
                                                     order.specialist.email])
        logger.info(f"{order} was declined")


@app.task(bind=True, default_retry_delay=10 * 60)
@try_except
def reminder_for_customer(self, order_id, site_name):
    """Remind a customer about an order.

    Args:
        self: current object
        order_id: order id
        site_name: site URL
    """
    order = Order.objects.get(id=order_id)
    if order.status == Order.StatusChoices.APPROVED:
        context = {"order": order, "site_name": site_name}

        RemindAboutOrderEmail(context=context).send([order.customer.email])

        logger.info(f"{order} reminding was sent to the {order.customer.get_full_name()}")


@app.task(bind=True, default_retry_delay=10 * 60)
@try_except
def send_message_for_specialist_consideration(self, order_id, site_name, is_secure):
    """Send approving order email.

    Args:
        self (object): current object
        order_id (int): order id
        site_name (str): site URL
        is_secure (bool): check connection protocol
    """
    order = Order.objects.get(id=1000)

    context = {"order": order,
               "protocol": "https" if is_secure else "http",
               "domain": site_name,
               "site_name": site_name,
               }

    ApprovingOrderEmail(context=context).send([order.specialist.email])

    logger.info(f"{order}: approving email was sent to the specialist "
                f"{order.specialist.get_full_name()}")
