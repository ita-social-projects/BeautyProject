"""Module with SpecialistScheduleView."""

from api.models import Order, Position, CustomUser, Service
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import timedelta, datetime, date
from api.serializers.order_serializers import OrderSerializer
from beauty.utils import string_to_time


def get_orders_for_specific_date(specialist, order_date):
    """Return active or approved orders.

    Filter them by certain specialist and specific date.
    """
    valid_order_statuses = [
        Order.StatusChoices.ACTIVE,
        Order.StatusChoices.APPROVED,
    ]

    return Order.objects.filter(
        specialist=specialist,
        status__in=valid_order_statuses,
        start_time__range=(order_date, order_date + timedelta(days=1)),
    )


def get_working_day(position, order_date):
    """."""
    weekdays = {
        0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu",
        4: "Fri", 5: "Sat", 6: "Sun",
    }

    order_day = order_date.weekday()
    return position.working_time[weekdays[order_day]]


def get_free_time(specialist, order_date, working_day):
    """Return list of time moments."""
    free_time = [
        string_to_time(time) for time in working_day
    ]
    orders = get_orders_for_specific_date(specialist, order_date)

    # Adds all time moments from orders (start and end) to free_time list.
    orders_time = [
        order_time
        for order in orders
        for order_time in (order.start_time.time(), order.end_time.time())
    ]

    free_time.extend(orders_time)

    # Remove values that are dublicated, including origin of dublicated value.
    # [1, 1, 2, 3, 4] then remove elements at 0 and 1 index.
    free_time = [time for time in free_time if free_time.count(time) == 1]
    free_time.sort()

    return free_time


def get_time_intervals(start_time, end_time):
    """Divides given time range in blocks by 15 min."""
    intervals = []

    start_time = datetime.combine(date.today(), start_time)
    end_time = datetime.combine(date.today(), end_time)

    # If only one aviable block
    if end_time >= start_time:
        time_range = end_time - start_time
    else:
        time_range = (end_time + timedelta(hours=24)) - start_time

    time_block = start_time

    for _ in range(time_range // timedelta(minutes=15) + 1):
        intervals.append(time_block.time())
        time_block += timedelta(minutes=15)

    return intervals


def get_free_time_for_customer(specialist, service, order_date, working_day):
    """Returns free time intervals."""
    free_time = get_free_time(specialist, order_date, working_day)

    new_free_time = []

    for start, end in zip(free_time[::2], free_time[1::2]):
        end = datetime.combine(datetime.today(), end)

        if end - datetime.combine(
            datetime.today(),
            start,
        ) >= service.duration:
            new_free_time.extend((start, (end - service.duration).time()))

    # First value is start of free time block, and second is end of block.
    free_time_blocks = [
        get_time_intervals(start, end)
        for start, end in
        zip(new_free_time[::2], new_free_time[1::2])
    ]

    return free_time_blocks


def get_free_time_specialist_for_owner(specialist, order_date,
                                       working_day, request):
    """Return list of free time blocks and orders."""
    specialist_schedule = get_free_time(specialist, order_date, working_day)

    specialist_schedule = [
        [start, end]
        for start, end in
        zip(specialist_schedule[::2], specialist_schedule[1::2])
    ]

    orders = get_orders_for_specific_date(specialist, order_date)

    # Needed of use insert method and access to list in same loop
    new_specialist_schedule = specialist_schedule.copy()

    for time in specialist_schedule:
        current_order = [
            OrderSerializer(order, context={"request": request}).data["url"]
            for order in orders
            if order.start_time.time() == time[1]
        ]

        if current_order:
            new_specialist_schedule.insert(
                new_specialist_schedule.index(time) + 1,
                current_order[0],
            )

    start_order = [
        OrderSerializer(order, context={"request": request}).data["url"]
        for order in orders
        if order.end_time.time() == specialist_schedule[0][0]
    ]

    if start_order:
        new_specialist_schedule.insert(0, start_order[0])

    return new_specialist_schedule


class SpecialistScheduleView(APIView):
    """View for displaying specialist's schedule."""

    def get(self, request, position_id,
            specialist_id, service_id, order_date):
        """GET method for retrieving schedule."""
        position = get_object_or_404(Position, id=position_id)
        specialist = get_object_or_404(CustomUser, id=specialist_id)
        service = get_object_or_404(Service, id=service_id)

        if specialist not in position.specialist.all():
            return Response(
                {"detail": "Such specialist doesn't hold position"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if service not in position.service_set.all():
            return Response(
                {"detail": "Such specialist doesn't have such service"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order_date.date() < date.today():
            return Response(
                {"detail": "You can't see schedule of the past days"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        working_day = get_working_day(position, order_date)

        if not working_day:
            return Response(
                {"detail": "Specialist is not working on this day"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            get_free_time_for_customer(
                specialist, service, order_date, working_day,
            ),
            status=status.HTTP_200_OK,
        )


class OwnerSpecialistScheduleView(APIView):
    """View for displaying specialist's schedule for owner."""

    def get(self, request, position_id, specialist_id, order_date):
        """GET method for retrieving schedule."""
        if not request.user.is_owner:
            return Response(
                {"detail": "Your are not an owner"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        position = get_object_or_404(Position, id=position_id)
        specialist = get_object_or_404(CustomUser, id=specialist_id)
        working_day = get_working_day(position, order_date)

        if request.user != position.business.owner:
            return Response(
                {"detail": "Your are not a position owner"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if specialist not in position.specialist.all():
            return Response(
                {"detail": "Such specialist doesn't hold position"},
                status=status.HTTP_404_NOT_FOUND,
            )

        schedule = get_free_time_specialist_for_owner(
            specialist,
            order_date,
            working_day,
            request,
        )

        if schedule:
            return Response(schedule, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Specialist is not working on this day"},
            status=status.HTTP_200_OK,
        )
