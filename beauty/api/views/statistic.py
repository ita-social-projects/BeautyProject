"""."""


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from api.models import Business, Order
from django.db.models import Avg, Sum, Count
from datetime import date, timedelta, datetime
from beauty.settings import TIME_ZONE
import pytz
from dateutil.relativedelta import relativedelta
from api.permissions import IsOwner


CET = pytz.timezone(TIME_ZONE)


class StatisticView(APIView):
    """."""

    permission_classes = (IsOwner,)

    def get(self, request, business_id):
        """."""
        business = get_object_or_404(Business, id=business_id)

        if business.owner != request.user:
            return Response(
                {"detail": "You don't have permission to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )

        specialists = business.get_all_specialists()

        time_interval = request.GET.get("timeInterval")
        if time_interval == "lastSevenDays":
            orders_date = date.today() - timedelta(days=6)

        elif time_interval == "currentMonth":
            orders_date = date.today().replace(day=1)

        elif time_interval == "lastThreeMonthes":
            today = datetime.now()
            orders_date = today - relativedelta(months=2)

        else:
            return Response(
                {"detail": "timeInterval value is not provided or invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        business_orders = business.get_orders_by_date(orders_date)

        orders_count_by_time = self._count_orders_by_time_interval(
            business_orders, time_interval, orders_date,
        )
        genaral_business_stat = self._general_statistic(business_orders)
        detailed_statistic = self._detailed_statistic(
            business_orders, specialists,
        )

        statistic = {
            "orders_count_by_time": orders_count_by_time,
            "general_statistic": genaral_business_stat,
            "business_specialists": detailed_statistic,
        }

        return Response(statistic, status=status.HTTP_200_OK)

    def _calc_sum_orders_price(self, orders_queryset):
        """."""
        orders_queryset = orders_queryset.filter(
            status=Order.StatusChoices.COMPLETED,
        )
        sum_price = orders_queryset.aggregate(
            total_price_orders=Sum("service__price"),
        )
        sum_price = sum_price["total_price_orders"]

        if sum_price is None:
            sum_price = 0

        return round(sum_price, 2)

    def _count_orders_by_status(self, orders):
        """."""
        return {
            status_str.capitalize(): orders.filter(status=status_int).count()
            for status_str, status_int in
            Order.StatusChoices.__members__.items()
        }

    def _count_orders_by_time_interval(self, orders, time_interval,
                                       orders_date):
        date_dict = {}
        if time_interval == "lastSevenDays" or time_interval == "currentMonth":

            new_date = orders_date
            while new_date != date.today() + timedelta(days=1):
                orders_for_date = orders.filter(
                    start_time__range=(new_date, new_date + timedelta(days=1)),
                ).count()
                date_dict[str(new_date)] = orders_for_date
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

        return date_dict

    def _get_most_least_pop_service(self, orders):
        count_services = orders.values("service__name").annotate(
            total=Count("service__name"),
        )

        if count_services:
            most_pop_service = max(
                count_services, key=lambda x: x["total"])["service__name"]
            least_pop_service = min(
                count_services, key=lambda x: x["total"])["service__name"]

        else:
            message = "No orders"
            most_pop_service, least_pop_service = (message,) * 2

        if most_pop_service == least_pop_service:
            message = "Not enought data"
            most_pop_service, least_pop_service = (message,) * 2

        return most_pop_service, least_pop_service

    def _general_statistic(self, business_orders):
        """."""
        business_profit = self._calc_sum_orders_price(business_orders)

        business_orders_count = business_orders.count()
        detailed_count = self._count_orders_by_status(business_orders)

        business_average_order = business_orders.aggregate(
            avg_price=Avg("service__price"),
        )["avg_price"]

        if not business_average_order:
            business_average_order = 0

        business_average_order = round(business_average_order, 2)

        most_pop_service, least_pop_service = self._get_most_least_pop_service(
            business_orders,
        )

        return {
            "detailed_count": detailed_count,
            "business_orders_count": business_orders_count,
            "business_profit": business_profit,
            "business_average_order": business_average_order,
            "most_popular_service": most_pop_service,
            "least_popular_service": least_pop_service,
        }

    def _detailed_statistic(self, business_orders, specialists):
        """."""
        business_specialists = {}

        for specialist in specialists:

            specialist_orders = business_orders.filter(specialist=specialist)
            specialist_orders_count = specialist_orders.count()
            orders_count_status = self._count_orders_by_status(
                specialist_orders,
            )
            specialist_orders_profit = self._calc_sum_orders_price(
                specialist_orders,
            )

            most_pop_serv, least_pop_serv = self._get_most_least_pop_service(
                specialist_orders,
            )

            specialist_stat = {
                "most_pop_service": most_pop_serv,
                "least_pop_service": least_pop_serv,
                "specialist_orders_count": specialist_orders_count,
                "specialist_orders_statuses": orders_count_status,
                "specialist_orders_profit": specialist_orders_profit,
            }

            business_specialists[specialist.get_full_name()] = specialist_stat

        return business_specialists
