"""This module is for testing schedule.

Tests for OwnerSpecialistScheduleView:
- Get valid schedule as owner
- Try to get schedule if not an owner
- Try get schedule if not position owner
- Get schedule by invalid specialist and position id
- Get schedule if there is order in the begining
- Get schedule if there is order in the midle
- Get schedule if there is order in the end

"""

from django.utils import timezone, dateformat
from datetime import datetime, timedelta
import pytz
from rest_framework.reverse import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from beauty.utils import string_to_time
from beauty.utils import generate_working_time
from api.serializers.order_serializers import OrderSerializer
from .factories import (BusinessFactory,
                        CustomUserFactory,
                        GroupFactory, OrderFactory,
                        PositionFactory, ServiceFactory)


class TestOwnerSpecialistScheduleView(TestCase):
    """TestCase to test OwnerSpecialistScheduleView."""

    def setUp(self):
        """Create business and 2 specialists."""
        self.groups = GroupFactory.groups_for_test()

        self.owner = CustomUserFactory.create(first_name="OwnerUser")
        self.specialist = CustomUserFactory.create(first_name="Specialist")
        self.groups.owner.user_set.add(self.owner)
        self.groups.specialist.user_set.add(self.specialist)

        self.owner_other = CustomUserFactory.create(first_name="OwnerUser")
        self.specialist_other = CustomUserFactory.create(
            first_name="Specialist",
        )
        self.groups.owner.user_set.add(self.owner_other)
        self.groups.specialist.user_set.add(self.specialist_other)

        self.start_time = "9:00"
        self.end_time = "13:00"
        self.duration = timedelta(minutes=10)
        self.working_time = generate_working_time(
            self.start_time,
            self.end_time,
        )
        self.date = timezone.datetime.now(tz=pytz.UTC)
        # If Sunday
        if self.date.weekday() == 6:
            self.date += timedelta(days=1, tz=pytz.UTC)

        self.working_time["Sun"] = []
        self.business = BusinessFactory.create(
            owner=self.owner,
            working_time=self.working_time,
        )
        self.position = PositionFactory.create(
            business=self.business,
            specialist=[self.specialist],
            working_time=self.working_time,
        )

        self.service = ServiceFactory.create(
            position=self.position,
            duration=self.duration,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

        self.url_kwargs = {
            "position_id": self.position.id,
            "specialist_id": self.specialist.id,
            "order_date": dateformat.format(self.date, "Y-m-d"),
        }
        self.url = reverse(
            "api:owner-specialist-schedule",
            kwargs=self.url_kwargs,
        )

    def test_get_schedule_as_owner(self):
        """Test get schedule if an owner."""
        response = self.client.get(
            path=self.url,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [[string_to_time(self.start_time), string_to_time(self.end_time)]],
        )

    def test_get_schedule_as_not_owner(self):
        """Test get schedule if not an owner."""
        user = CustomUserFactory.create()
        self.client.force_authenticate(user=user)
        response = self.client.get(
            path=self.url,
        )
        self.assertEqual(response.status_code, 400)

    def test_get_schedule_wrong_position(self):
        """Test if not position owner."""
        position = PositionFactory.create()
        self.url_kwargs["position_id"] = position.id
        self.url = reverse(
            "api:owner-specialist-schedule",
            kwargs=self.url_kwargs,
        )
        response = self.client.get(
            path=self.url,
        )
        self.assertEqual(response.status_code, 400)

    def test_get_schedule_not_specialist_owner(self):
        """Test if not specialist owner."""
        position = PositionFactory.create(specialist=[self.specialist_other])
        self.url_kwargs["position_id"] = position.id
        self.url_kwargs["specialist_id"] = self.specialist_other.id
        self.url = reverse(
            "api:owner-specialist-schedule",
            kwargs=self.url_kwargs,
        )

        response = self.client.get(
            path=self.url,
        )
        self.assertEqual(response.status_code, 400)

    def test_get_schedule_invalid_specialist(self):
        """Test if not specialist not in position."""
        PositionFactory.create(specialist=[self.specialist_other])
        self.url_kwargs["specialist_id"] = self.specialist_other.id
        self.url = reverse(
            "api:owner-specialist-schedule",
            kwargs=self.url_kwargs,
        )

        response = self.client.get(
            path=self.url,
        )
        self.assertEqual(response.status_code, 404)

    def test_get_schedule_order_begining(self):
        """Test if order in the begining of working day."""
        order = OrderFactory.create(
            start_time=datetime.combine(
                self.date,
                string_to_time(self.start_time),
                tzinfo=pytz.UTC,
            ),
            service=self.service,
            specialist=self.specialist,
        )

        response = self.client.get(
            path=self.url,
        )

        order_serialized = OrderSerializer(
            order,
            context={"request": response.wsgi_request}).data["url"]

        result = [
            order_serialized,
            [order.end_time.time(),
             string_to_time(self.end_time)],
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, result)

    def test_get_schedule_order_midle(self):
        """Test if order in the midle of working day."""
        order = OrderFactory.create(
            start_time=datetime.combine(
                self.date,
                (datetime.combine(
                    self.date,
                    string_to_time(self.start_time),
                    tzinfo=pytz.UTC,
                ) + self.duration).time(),
                tzinfo=pytz.UTC,
            ),
            service=self.service,
            specialist=self.specialist,
        )

        response = self.client.get(
            path=self.url,
        )

        order_serialized = OrderSerializer(
            order,
            context={"request": response.wsgi_request}).data["url"]

        result = [
            [string_to_time(self.start_time), order.start_time.time()],
            order_serialized,
            [order.end_time.time(), string_to_time(self.end_time)],
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, result)

    def test_get_schedule_order_ending(self):
        """Test if order in the ending of working day."""
        order = OrderFactory.create(
            start_time=datetime.combine(
                self.date,
                (datetime.combine(
                    self.date,
                    string_to_time(self.end_time),
                    tzinfo=pytz.UTC,
                ) - self.duration).time(),
                tzinfo=pytz.UTC,
            ),
            service=self.service,
            specialist=self.specialist,
        )

        response = self.client.get(
            path=self.url,
        )

        order_serialized = OrderSerializer(
            order,
            context={"request": response.wsgi_request}).data["url"]

        result = [
            [string_to_time(self.start_time), order.start_time.time()],
            order_serialized,
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, result)
