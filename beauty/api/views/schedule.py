"""Module with SpecialistScheduleView."""

from api.models import Business, Order, Position
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
    for _ in range(int(time_range / timedelta(minutes=30))):
        intervals.append(time_block.time())
        time_block += timedelta(minutes=15)

    return intervals


def get_free_time_intervals(position):
    """Returns free time intervals."""
    free_time = [position.start_time, position.end_time]
    orders = Order.objects.filter(service__position=position, status=3)

    for order in orders:
        start_current = order.start_time.time()
        end_current = order.end_time.time()
        free_time.extend([start_current, end_current])
        free_time.sort()

    return free_time


class SpecialistScheduleView(APIView):
    """View for displaying specialist's schedule."""

    def get(self, request, position_id, business_id=1, specialist_id=1):
        """GET method for retrieving schedule."""
        position = Position.objects.get(id=position_id)

        return Response(
            get_free_time_intervals(position),
            status=status.HTTP_200_OK,
        )

        business = get_object_or_404(
            Business, id=business_id,
        )

        try:
            position = business.position_set.get(
                id=position_id,
            )

        except Position.DoesNotExist:
            return Response(
                "Such position does not exist",
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            get_time_intervals(position.start_time, position.start_time),
            status=status.HTTP_200_OK,
        )
