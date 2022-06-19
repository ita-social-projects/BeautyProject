"""Module with SpecialistScheduleView."""

from api.models import Order, Position, CustomUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import timedelta, datetime, date


def get_time_intervals(start_time, end_time):
    """Divides given time range in blocks by 15 min."""
    intervals = []

    start_time = datetime.combine(date.today(), start_time)
    end_time = datetime.combine(date.today(), end_time)

    if end_time > start_time:
        time_range = end_time - start_time
    else:
        time_range = (end_time + timedelta(hours=24)) - start_time

    time_block = start_time
    for _ in range(time_range // timedelta(minutes=15) - 3):
        intervals.append(time_block.time())
        time_block += timedelta(minutes=15)

    return intervals


def get_free_time_intervals(position, specialist, order_date):
    """Returns free time intervals."""
    free_time = [position.start_time, position.end_time]

    valid_order_statuses = [
        Order.StatusChoices.ACTIVE,
        Order.StatusChoices.APPROVED,
    ]

    next_day_order_date = order_date + timedelta(days=1)

    # Get all not canceled orders for position.
    orders = Order.objects.filter(
        specialist=specialist,
        status__in=valid_order_statuses,
        start_time__range=(order_date, next_day_order_date),
    )

    # Adds all time moments from orders (start and end) to free_time list.
    free_time.extend([order_time for order in orders
                      for order_time in (
                          order.start_time.time(),
                          order.end_time.time(),
                      )])

    free_time.sort()

    # Remove values that are dublicated, including origin of dublicated value.
    # [1, 1, 2, 3, 4] then remove elements at 0 and 1 index.
    free_time = [time for time in free_time if free_time.count(time) == 1]

    # First value is start of free time block, and second is end of block.
    free_time_blocks = [get_time_intervals(free_time[i], free_time[i + 1])
                        for i in range(0, len(free_time) - 1, 2)]

    return free_time_blocks


class SpecialistScheduleView(APIView):
    """View for displaying specialist's schedule."""

    def get(self, request, position_id, specialist_id, order_date):
        """GET method for retrieving schedule."""
        position = get_object_or_404(Position, id=position_id)
        specialist = get_object_or_404(CustomUser, id=specialist_id)

        if specialist in position.specialist.all():
            return Response(
                get_free_time_intervals(position, specialist, order_date),
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
