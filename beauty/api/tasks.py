"""Module with a celery tasks."""
import smtplib

from beauty.celery import app
from api.models import Order
from celery.utils.log import get_task_logger

from beauty.utils import AutoDeclineOrderEmail


logger = get_task_logger(__name__)


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

            AutoDeclineOrderEmail(context=context).send([order.customer.email])
            AutoDeclineOrderEmail(context=context).send([order.specialist.email])

            logger.info(f"{order} was declined")
    except Order.DoesNotExist:
        logger.info(f"Order with id={order_id} does not exist")
    except smtplib.SMTPException as ex:
        self.retry(exc=ex, countdown=5)
    except Exception as exc:
        logger.info(f"Error: {exc.args[0]}")
