"""Module with a celery tasks."""

import logging
import smtplib
from beauty.celery import app
from api.models import Order
from beauty.utils import (AutoDeclineOrderEmail, RemindAboutOrderEmail, ApprovingOrderEmail)


logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=5 * 60)
def change_order_status_to_decline(self, order_id, site_name):
    """Change new order status to the declined.

     If a specialist did not approve or decline an order during 3 hours it declines automatic.

    Args:
        self: current object
        order_id: order id
        site_name: site URL
    """
    try:
        order = Order.objects.get(id=order_id)
        if order.status == Order.StatusChoices.ACTIVE:
            order.status = Order.StatusChoices.DECLINED
            order.save()
            context = {"order": order, "site_name": site_name}

            AutoDeclineOrderEmail(context=context).send([order.customer.email,
                                                         order.specialist.email])

            logger.info(f"{order} was declined")

    except Order.DoesNotExist:
        logger.info(f"Order with id={order_id} does not exist")
    except smtplib.SMTPException as ex:
        logger.info(f"SMTPException: {ex.args[0]}")
        self.retry(exc=ex, countdown=5)
    except Exception as ex:
        logger.info(f"Error: {ex.args[0]}")
        self.retry(exc=ex, countdown=5)


@app.task(bind=True, default_retry_delay=10 * 60)
def reminder_for_customer(self, order_id, site_name):
    """Remind a customer about an order.

    Args:
        self: current object
        order_id: order id
        site_name: site URL
    """
    try:
        order = Order.objects.get(id=order_id)
        if order.status == Order.StatusChoices.APPROVED:
            context = {"order": order, "site_name": site_name}

            RemindAboutOrderEmail(context=context).send([order.customer.email])

            logger.info(f"{order} reminding was sent to the {order.customer.get_full_name()}")

    except Order.DoesNotExist:
        logger.info(f"Order with id={order_id} does not exist")
    except smtplib.SMTPException as ex:
        logger.info(f"SMTPException: {ex.args[0]}")
        self.retry(exc=ex, countdown=5)
    except Exception as ex:
        logger.info(f"Error: {ex.args[0]}")
        self.retry(exc=ex, countdown=5)


@app.task(bind=True, default_retry_delay=10 * 60)
def send_message_for_specialist_consideration(self, order_id, site_name, is_secure):
    """Send approving order email.

    Args:
        self (object): current object
        order_id (int): order id
        site_name (str): site URL
        is_secure (bool): check connection protocol
    """
    try:
        order = Order.objects.get(id=order_id)

        context = {"order": order,
                   "protocol": "https" if is_secure else "http",
                   "domain": site_name,
                   "site_name": site_name,
                   }

        ApprovingOrderEmail(context=context).send([order.specialist.email])

        logger.info(f"{order}: approving email was sent to the specialist "
                    f"{order.specialist.get_full_name()}")

    except Order.DoesNotExist:
        logger.info(f"Order with id={order_id} does not exist")
    except smtplib.SMTPException as ex:
        logger.info(f"SMTPException: {ex.args[0]}")
        self.retry(exc=ex, countdown=5)
    except Exception as ex:
        logger.info(f"Error: {ex.args[0]}")
        self.retry(exc=ex, countdown=5)
