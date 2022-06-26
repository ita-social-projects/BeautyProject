"""Module with a celery tasks."""

from beauty.celery import app
from api.models import Order
from celery.utils.log import get_task_logger

from beauty.utils import StatusOrderEmail

logger = get_task_logger(__name__)


@app.task
def change_order_status_to_decline(order_id, site_name):
    """Change new order status to the declined.

     If a specialist did not approve or decline an order during 3 hours it declines automatic.

    Args:
        order_id: order id
        site_name: site URL
    """
    try:
        order = Order.objects.get(id=order_id)
        if order.status == Order.StatusChoices.ACTIVE:
            order.status = Order.StatusChoices.DECLINED
            order.save()
            StatusOrderEmail(
                context={"order": order, "site_name": site_name}).send([order.customer.email])
            logger.info(f"{order} was declined")
    except Order.DoesNotExist:
        logger.info(f"Order with id={order_id} does not exist")
    except Exception as exc:
        logger.info(f"Error: {exc.args[0]}")
