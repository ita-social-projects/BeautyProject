"""This module is for testing statistic for certain business.

Tests for StatisticView:
- User is not authentificated.
- User does not belong to Owner group.
- User doesn't own business, statistic of which, he wants to see.
- No timeInterval value in request.
- Statistic for lastSevenDays.
- Statistic for currentMonth.
- Statistic for lastThreeMonthes.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from api.tests.factories import (
    CustomUserFactory, BusinessFactory, GroupFactory, OrderFactory,
    PositionFactory, ServiceFactory,
)
from datetime import datetime, date, time, timedelta
from beauty.settings import TIME_ZONE
from pytz import timezone

CET = timezone(TIME_ZONE)


class StatisticTest(TestCase):
    """Class with tests for StatisticView."""

    def setUp(self) -> None:
        """Set up required objects for tests."""
        self.groups = GroupFactory.groups_for_test()

        self.owner = CustomUserFactory.create()
        self.specialist = CustomUserFactory.create()
        self.customer = CustomUserFactory.create()
        self.groups.owner.user_set.add(self.owner)
        self.groups.specialist.user_set.add(self.specialist)
        self.groups.customer.user_set.add(self.specialist)

        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

        self.business = BusinessFactory.create(owner=self.owner)
        self.position = PositionFactory.create(business=self.business)
        self.position.specialist.add(self.specialist)
        self.service = ServiceFactory.create(position=self.position)

    def test_not_auth_user(self):
        """Test if user is not authenticated."""
        self.client.force_authenticate(user=None)
        response = self.client.get(
            reverse(
                "api:statistic-of-business",
                kwargs={"business_id": self.business.id},
            ),
        )

        self.assertEqual(response.status_code, 401)

    def test_not_owner_group(self):
        """Test if user doesn't belong to Owner group."""
        self.groups.owner.user_set.set([])
        response = self.client.get(
            reverse(
                "api:statistic-of-business",
                kwargs={"business_id": self.business.id},
            ),
        )

        self.assertEqual(response.status_code, 403)

    def test_not_business_owner(self):
        """Test if user is not an owner of a business."""
        self.specialist = CustomUserFactory.create()
        self.business.owner = self.specialist
        self.business.save()

        response = self.client.get(
            reverse(
                "api:statistic-of-business",
                kwargs={"business_id": self.business.id},
            ),
        )

        self.assertEqual(response.status_code, 403)

    def test_no_time_interval(self):
        """Test if not timeInterval param was provided."""
        response = self.client.get(
            reverse(
                "api:statistic-of-business",
                kwargs={"business_id": self.business.id},
            ),
        )

        self.assertEqual(response.status_code, 400)

    def test_wrong_time_interval(self):
        """Test if invalid intervalTime was provided."""
        url = reverse(
            "api:statistic-of-business",
            kwargs={"business_id": self.business.id},
        )
        url += "?timeInterval=wrong"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_last_seven_days(self):
        """Test valid request and its response.

        lastSevenDays timeInterval value was provided. Check response without
        and with order. Test if counting orders accoring to the time is
        correct.
        """
        url = reverse(
            "api:statistic-of-business",
            kwargs={"business_id": self.business.id},
        )
        url += "?timeInterval=lastSevenDays"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.data
        for order_count in data["line_chart_data"]["data"]:
            with self.subTest():
                self.assertEqual(order_count, 0)

        general_statistic = [
            {
                "business_orders_count": 0,
                "business_profit": 0,
                "business_average_order": 0,
                "most_popular_service": "No orders",
                "least_popular_service": "No orders",
                "active": 0,
                "completed": 0,
                "cancelled": 0,
                "approved": 0,
                "declined": 0,
            },
        ]

        self.assertEqual(data["general_statistic"], general_statistic)

        start_time = datetime.combine(date.today(), time(hour=11, minute=35))
        start_time = CET.localize(start_time)

        OrderFactory.create(
            customer=self.customer, specialist=self.specialist,
            service=self.service, start_time=start_time,
        )

        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data2 = response2.data
        self.assertNotEqual(data, data2)

        data2 = response2.data
        self.assertNotEqual(data, data2)

        start_time -= timedelta(days=11)
        OrderFactory.create(
            customer=self.customer, specialist=self.specialist,
            service=self.service, start_time=start_time,
        )

        response3 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data3 = response3.data
        self.assertEqual(data2, data3)

    def test_current_month(self):
        """Test valid requests and its responses.

        currentMonth timeInterval value was provided. Check response without
        and with order. Test if counting orders accoring to the time is
        correct.
        """
        url = reverse(
            "api:statistic-of-business",
            kwargs={"business_id": self.business.id},
        )
        url += "?timeInterval=currentMonth"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.data

        start_time = datetime.combine(
            datetime.today() - timedelta(days=11),
            time(hour=11, minute=35),
        )
        start_time = CET.localize(start_time)

        OrderFactory.create(
            customer=self.customer, specialist=self.specialist,
            service=self.service, start_time=start_time,
        )

        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data2 = response2.data
        self.assertNotEqual(data, data2)

        start_time -= timedelta(days=31)
        OrderFactory.create(
            customer=self.customer, specialist=self.specialist,
            service=self.service, start_time=start_time,
        )

        response3 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data3 = response3.data
        self.assertEqual(data2, data3)

    def test_last_three_monthes(self):
        """Test valid requests and its responses.

        lastThreeMonthes timeInterval value was provided. Check without and
        with order. Test if counting orders accoring to the time is
        correct.
        """
        url = reverse(
            "api:statistic-of-business",
            kwargs={"business_id": self.business.id},
        )
        url += "?timeInterval=lastThreeMonthes"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.data

        start_time = datetime.combine(
            datetime.today() - timedelta(days=32),
            time(hour=11, minute=35),
        )
        start_time = CET.localize(start_time)

        OrderFactory.create(
            customer=self.customer, specialist=self.specialist,
            service=self.service, start_time=start_time,
        )

        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data2 = response2.data
        self.assertNotEqual(data, data2)
        self.assertEqual(len(data["line_chart_data"]["labels"]), 4)

        start_time -= timedelta(days=90)
        OrderFactory.create(
            customer=self.customer, specialist=self.specialist,
            service=self.service, start_time=start_time,
        )

        response3 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data3 = response3.data
        self.assertEqual(data2, data3)
