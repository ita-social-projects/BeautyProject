"""Module with SpecialistScheduleView."""

from api.models import Position, Business
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


class SpecialistScheduleView(APIView):
    """View for displaying specialist's schedule."""

    def get(self, request, specialist_id, business_id, position_id):
        """GET method for retrieving schedule."""
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
