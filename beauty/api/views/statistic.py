"""Module with StatisticView and utilities for this view."""


from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Business, Order
from django.db.models import Avg, Sum, Count
from datetime import date, timedelta, datetime
from beauty.settings import TIME_ZONE
import pytz
from dateutil.relativedelta import relativedelta
from api.permissions import IsOwner, IsAdminOrThisBusinessOwner
from beauty.utils import Chart
from api.serializers.chart_serializers import ChartSerializer
import logging
from enum import Enum


CET = pytz.timezone(TIME_ZONE)
logger = logging.getLogger(__name__)


class TimeIntervals(Enum):
    """Enum class which provides timeintervals constants."""
    CURRENT_WEEK = "lastSevenDays"
    CURRENT_MONTH = "currentMonth"
    LAST_THREE_MONTHES = "lastThreeMonthes"


class StatisticView(GenericAPIView):
    """Return data with general statistic statistic of each specialist.

    _line_chart: return labels and data for building chart
    _general_statistic: return general statistic of the business
    _detailed_statistic: return statistic about each specialist
    get: return results of all mentioned above methods
    """

    permission_classes = (IsOwner & IsAdminOrThisBusinessOwner,)
    queryset = Business.objects.all()
    lookup_url_kwarg = "business_id"

    def get(self, request, business_id):
        """Return statistic, according to the timeInterval value.

        Check if timeInterval value is provided and correct, return data for
        chart, business table and specialists table.
        """
        business = self.get_object()

        time_interval = request.GET.get("timeInterval")
        if time_interval == TimeIntervals.CURRENT_WEEK.value:
            orders_date = date.today() - timedelta(days=6)

        elif time_interval == TimeIntervals.CURRENT_MONTH.value:
            orders_date = date.today() - relativedelta(months=1)

        elif time_interval == TimeIntervals.LAST_THREE_MONTHES.value:
            today = datetime.now()
            orders_date = today - relativedelta(months=3)

        else:
            return Response(
                {"detail": "timeInterval value is not provided or invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        specialists = business.get_all_specialists()
        business_orders = business.get_orders_by_date(
            orders_date,
        )

        orders_count_by_time = count_orders_by_time_interval(
            business_orders, time_interval, orders_date,
        )

        labels = [label for label in orders_count_by_time]
        data = [el for el in orders_count_by_time.values()]

        line_chart_data = self._line_chart(labels, data)

        genaral_business_stat = self._general_statistic(business_orders)
        detailed_statistic = self._detailed_statistic(
            business_orders, specialists,
        )

        statistic = {
            "line_chart_data": line_chart_data,
            "general_statistic": genaral_business_stat,
            "business_specialists": detailed_statistic,
        }

        logger.info(f"Statstic about business {business} was fetched.")
        return Response(statistic, status=status.HTTP_200_OK)

    def _line_chart(self, labels, data):
        line_chart = Chart(labels, data)
        logger.info("Got labels and data for chart.")
        return ChartSerializer(line_chart).data

    def _general_statistic(self, business_orders):
        """Return general statistic about business.

        This data is used for building business table on a FrontEnd statistic
        page.
        """
        business_profit = calc_sum_orders_price(business_orders)

        business_orders_count = business_orders.count()
        detailed_count = count_orders_by_status(business_orders)

        business_average_order = business_orders.aggregate(
            avg_price=Avg("service__price"),
        )["avg_price"]

        if not business_average_order:
            business_average_order = 0

        business_average_order = round(business_average_order, 2)

        most_pop_service, least_pop_service = get_most_least_pop_service(
            business_orders,
        )

        result = {
            "business_orders_count": business_orders_count,
            "business_profit": business_profit,
            "business_average_order": business_average_order,
            "most_popular_service": most_pop_service,
            "least_popular_service": least_pop_service,
        }

        result.update(detailed_count)

        logger.info("Got general statistic about business.")
        return [result]

    def _detailed_statistic(self, business_orders, specialists):
        """Return detailed statistic about businesses' specialists.

        This data is used for building specialist table on a FrontEnd statistic
        page.
        """
        business_specialists = []

        for specialist in specialists.iterator():

            specialist_orders = business_orders.filter(specialist=specialist)
            specialist_orders_count = specialist_orders.count()
            orders_count_status = count_orders_by_status(
                specialist_orders,
            )
            specialist_orders_profit = calc_sum_orders_price(
                specialist_orders,
            )

            most_pop_serv, least_pop_serv = get_most_least_pop_service(
                specialist_orders,
            )

            specialist_stat = {
                "specialist_name": specialist.get_full_name(),
                "most_pop_service": most_pop_serv,
                "least_pop_service": least_pop_serv,
                "specialist_orders_count": specialist_orders_count,
                "specialist_orders_profit": specialist_orders_profit,
            }

            specialist_stat.update(orders_count_status)
            business_specialists.append(specialist_stat)

        logger.info("Got detailed statistic about each specilalist.")
        return business_specialists


def calc_sum_orders_price(orders_queryset):
    """Return sum of order's prices.

    Args:
        orders_queryset (QuerySet[Order])

    Returns:
        int: total of order's prices
    """
    orders_queryset = orders_queryset.filter(
        status=Order.StatusChoices.COMPLETED,
    )
    sum_price = orders_queryset.aggregate(
        total_price_orders=Sum("service__price"))["total_price_orders"]

    if sum_price is None:
        sum_price = 0

    logger.info("Got total price of orders.")
    return round(sum_price, 2)


def count_orders_by_status(orders):
    """Return dict with amount of orders depending on their status.

    Args:
        orders (QuerySet[Order])

    Returns:
        dict: dict with orders amount, counted by its statuses
    """
    logger.info("Counted orders by statuses")
    return {
        status_str.lower(): orders.filter(status=status_int).count()
        for status_str, status_int in
        Order.StatusChoices.__members__.items()
    }


def count_orders_by_time_interval(orders, time_interval,
                                  orders_date):
    """Return amount of orders starting from certain date.

    Args:
        orders (QuerySet[Order])
        time_interval (str): time from which it is needed to count orders
        orders_date (date)

    Returns:
        dict: keys - time stamps and value - count of orders
    """
    date_dict = {}
    time_with_date = [
        time_interval == TimeIntervals.CURRENT_WEEK.value,
        time_interval == TimeIntervals.CURRENT_MONTH.value,
    ]

    if any(time_with_date):
        orders_date = datetime.combine(orders_date, datetime.min.time())
        new_date = CET.localize(orders_date)

        while new_date.date() != date.today() + timedelta(days=1):
            orders_for_date = orders.filter(
                start_time__range=(new_date, new_date + timedelta(days=1)),
            ).count()
            date_str = str(new_date.day) + " " + new_date.strftime("%B")[:3]
            date_dict[date_str] = orders_for_date
            new_date += timedelta(days=1)

    else:
        new_date = orders_date
        current_month = date.today().month

        while new_date.month != current_month + 1:
            orders_for_date = orders.filter(
                start_time__month=new_date.month,
            ).count()
            date_dict[new_date.strftime("%B")] = orders_for_date
            new_date += relativedelta(months=1)

    logger.info("Counted orders by time interval")
    return date_dict


def get_most_least_pop_service(orders):
    """Return most and least popular service according to the orders.

    Args:
        orders (QuerySet[Order])

    Returns:
        tuple: tuple of two elements: most and least popular service
    """
    count_services = orders.values("service__name").annotate(
        total=Count("service__name"),
    )

    if count_services:
        most_pop_service = max(
            count_services, key=lambda x: x["total"])["service__name"]
        least_pop_service = min(
            count_services, key=lambda x: x["total"])["service__name"]

        if len(orders) < 3:
            message = "Not enought data"
            most_pop_service, least_pop_service = (message,) * 2

    else:
        message = "No orders"
        most_pop_service, least_pop_service = (message,) * 2

    logger.info("Got most and least popular services")
    return most_pop_service, least_pop_service
