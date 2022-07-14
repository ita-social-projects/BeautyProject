"""This module is for testing schedule of specialist.

Tests for TestSpecialistSchedule:
- Set up all required objects for the tests;
- Test if endpoint return 404 response for invalid specialist;
- Test if endpoint return 404 response for invalid service;
- Test if endpoint return 400 response for weekend;
- Test if endpoint return 400 response for past days;
- Test if endpoint return 200 response for valid data wigth and without order.
"""


from datetime import date, timedelta, datetime, time
import json
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from api.tests.factories import (CustomUserFactory, PositionFactory,
                                 ServiceFactory, OrderFactory)


def get_next_desired_day(day_int: int) -> date:
    """Return date of desired day, Monday for example, for the next week.

    day_int: number of day, for Monady is 0.
    """
    date_today = date.today()
    next_desired_day = date_today

    while next_desired_day.weekday() != day_int:
        next_desired_day += timedelta(days=1)

    return next_desired_day


class TestSpecialistSchedule(TestCase):
    """TestCase for schedule.py. SpecialistSchedule view."""

    position_schedule = {
        "Mon": ["13:10", "16:30"],
        "Tue": ["13:10", "16:30"],
        "Wed": ["13:10", "16:30"],
        "Thu": ["13:10", "16:30"],
        "Fri": ["13:10", "16:30"],
        "Sat": ["13:10", "15:30"],
        "Sun": [],
    }

    def setUp(self) -> None:
        """Set up all required objects for the tests."""
        self.position = PositionFactory.create(
            working_time=self.position_schedule,
        )
        self.service1 = ServiceFactory.create()
        self.service2 = ServiceFactory.create(
            position=self.position, duration=timedelta(minutes=15),
        )

        self.specialist1 = CustomUserFactory.create()
        self.specialist2 = CustomUserFactory.create()
        self.position.specialist.add(self.specialist2)

    def test_schedule_invalid_specialist(self):
        """Test if endpoint return 404 response for invalid specialist."""
        response = self.client.get(
            path=reverse(
                "api:specialist-schedule",
                kwargs={
                    "position_id": self.position.id,
                    "specialist_id": self.specialist1.id,
                    "service_id": self.service1.id,
                    "order_date": get_next_desired_day(3),
                },
            ),
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data,
            {"detail": "Such specialist doesn't hold position"},
        )

    def test_schedule_invalid_service(self):
        """Test if endpoint return 404 response for invalid service."""
        response = self.client.get(
            path=reverse(
                "api:specialist-schedule",
                kwargs={
                    "position_id": self.position.id,
                    "specialist_id": self.specialist2.id,
                    "service_id": self.service1.id,
                    "order_date": get_next_desired_day(3),
                },
            ),
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data,
            {"detail": "Such specialist doesn't have such service"},
        )

    def test_schedule_invalid_day(self):
        """Test if endpoint return 400 response for weekend."""
        response = self.client.get(
            path=reverse(
                "api:specialist-schedule",
                kwargs={
                    "position_id": self.position.id,
                    "specialist_id": self.specialist2.id,
                    "service_id": self.service2.id,
                    "order_date": get_next_desired_day(6),
                },
            ),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {"detail": "Specialist is not working on this day"},
        )

    def test_schedule_invalid_date_past(self):
        """Test if endpoint return 400 response for past days."""
        response = self.client.get(
            path=reverse(
                "api:specialist-schedule",
                kwargs={
                    "position_id": self.position.id,
                    "specialist_id": self.specialist2.id,
                    "service_id": self.service2.id,
                    "order_date": "2022-06-22",
                },
            ),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {"detail": "You can't see schedule of the past days"},
        )

    def test_schedule_valid(self):
        """Test if endpoint return 200 response for valid data.

        With and without order.
        """
        response1 = self.client.get(
            path=reverse(
                "api:specialist-schedule",
                kwargs={
                    "position_id": self.position.id,
                    "specialist_id": self.specialist2.id,
                    "service_id": self.service2.id,
                    "order_date": get_next_desired_day(3),
                },
            ),
        )

        self.assertEqual(response1.status_code, 200)

        order_time = timezone.make_aware(datetime.combine(
            get_next_desired_day(3), time(hour=13, minute=25),
        ))
        self.order1 = OrderFactory.create(
            start_time=order_time,
            specialist=self.specialist2,
            service=self.service2,
        )

        response2 = self.client.get(
            path=reverse(
                "api:specialist-schedule",
                kwargs={
                    "position_id": self.position.id,
                    "specialist_id": self.specialist2.id,
                    "service_id": self.service2.id,
                    "order_date": get_next_desired_day(3),
                },
            ),
        )

        self.assertEqual(response2.status_code, 200)
        self.assertNotEqual(response1.data, response2.data)

        for time_interval in response2:
            with self.subTest():
                self.assertNotIn(order_time.time(), json.loads(time_interval))
