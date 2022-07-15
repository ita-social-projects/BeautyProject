"""This module is for testing BusinessRUDView when changing working time.

Test includes:
- SetUp method adds needed data for tests;
- Patch specific day;
- Reduce time in different day then order;
- Reduce working time in day, when order is;
- Change day to weekend when order is;
"""
import calendar
import pytz
from django.core import mail
from django.utils.timezone import localtime
from datetime import (date, datetime, timedelta)
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.models import Business
from beauty.settings import EMAIL_HOST_USER, TIME_ZONE
from beauty.utils import string_to_time, time_to_string
from .factories import (BusinessFactory,
                        CustomUserFactory,
                        GroupFactory,
                        OrderFactory,
                        PositionFactory,
                        ServiceFactory)


class TestUpdateWorkingTime(TestCase):
    """TestCase to test PositionRetrieveUpdateDestroyView."""

    def setUp(self):
        """Create order and all it needs."""
        self.groups = GroupFactory.groups_for_test()
        self.specialist = CustomUserFactory(first_name="UserSpecialist")
        self.groups.specialist.user_set.add(self.specialist)
        self.owner = CustomUserFactory(first_name="Owner")
        self.groups.owner.user_set.add(self.owner)

        self.business = BusinessFactory.create(owner=self.owner)
        self.position = PositionFactory.create(
            business=self.business,
            specialist=[self.specialist],
        )
        self.service = ServiceFactory.create(
            position=self.position,
            duration=timedelta(seconds=10 * 60),
        )
        self.weekday = "Mon"
        self.weekday_id = 0

        self.date = date.today() + timedelta(days=1)
        while(self.date.weekday() != self.weekday_id):
            self.date += timedelta(days=1)
        self.time = string_to_time(self.business.working_time[self.weekday][0])
        self.order = OrderFactory.create(
            specialist=self.specialist,
            service=self.service,
            start_time=datetime.combine(self.date, self.time, tzinfo=pytz.timezone(TIME_ZONE)),
        )

        self.pk = self.business.id

        self.url = reverse(viewname="api:business-detail", kwargs={"pk": self.pk})

        self.client = APIClient()
        self.client.force_authenticate(user=self.business.owner)

    def test_patch_specific_day(self):
        """Patch only one day."""
        changed_time = (self.order.start_time - timedelta(seconds=10 * 60)).time()
        data = {
            self.weekday: [
                time_to_string(changed_time),
                self.business.working_time[self.weekday][1],
            ],
        }
        response = self.client.patch(
            path=self.url,
            data=data,
        )
        self.assertEqual(len(Business.objects.all()[0].working_time), 7)
        self.assertEqual(mail.outbox, [])
        self.assertEqual(response.status_code, 200)

    def test_patch_not_order_day(self):
        """Patch and reduce time not in order day."""
        changed_time = (self.order.start_time + timedelta(seconds=10 * 60)).time()
        next_day = calendar.day_name[(self.order.start_time + timedelta(days=1)).weekday()]
        data = {
            next_day: [
                time_to_string(changed_time),
                self.business.working_time[self.weekday][1],
            ],
        }
        response = self.client.patch(
            path=self.url,
            data=data,
        )
        self.assertEqual(len(Business.objects.all()[0].working_time), 7)
        self.assertEqual(mail.outbox, [])
        self.assertEqual(response.status_code, 200)

    def test_patch_reduce_order_day(self):
        """Patch and reduce time in order day."""
        changed_time = localtime(self.order.start_time + timedelta(seconds=10 * 60)).time()
        data = {
            self.weekday: [
                time_to_string(changed_time),
                self.business.working_time[self.weekday][1],
            ],
        }
        response = self.client.patch(
            path=self.url,
            data=data,
        )
        self.assertEqual(len(Business.objects.all()[0].working_time), 7)
        self.assertListEqual(
            [self.order.customer.email, self.specialist.email],
            mail.outbox[0].to,
        )
        self.assertEqual(
            EMAIL_HOST_USER,
            mail.outbox[0].from_email,
        )
        self.assertEqual(response.status_code, 200)

    def test_patch_weekend_order_day(self):
        """Patch adn reduce time not in order day."""
        data = {
            self.weekday: [],
        }
        response = self.client.patch(
            path=self.url,
            data=data,
        )
        self.assertEqual(len(Business.objects.all()[0].working_time), 7)
        self.assertListEqual(
            [self.order.customer.email, self.specialist.email],
            mail.outbox[0].to,
        )
        self.assertEqual(
            EMAIL_HOST_USER,
            mail.outbox[0].from_email,
        )
        self.assertEqual(response.status_code, 200)
