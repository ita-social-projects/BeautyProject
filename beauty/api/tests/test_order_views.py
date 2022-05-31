"""This module is for testing order's serializers.

Tests for OrderSerializer:

"""

from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api.serializers.order_serializers import OrderSerializer
from api.views import (OrderListCreateView,
                       OrderRetrieveUpdateDestroyView,
                       OrderApprovingTokenGenerator)
from .factories import *


class TestOrderListCreateView(TestCase):
    """This class represents a Test case and has all the tests for OrderListCreateView."""

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.Serializer = OrderSerializer

        self.groups = GroupFactory.groups_for_test()
        self.specialist = CustomUserFactory(first_name="UserSpecialist")
        self.customer = CustomUserFactory(first_name="UserCustomer")
        self.position = PositionFactory(name="Position_1")
        self.service = ServiceFactory(name="Service_1", position=self.position)

        self.groups.specialist.user_set.add(self.specialist)
        self.groups.customer.user_set.add(self.customer)
        self.position.specialist.add(self.specialist)

        self.view = OrderListCreateView
        self.client = APIClient()
        self.client.force_authenticate(user=self.customer)

        self.data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                     'specialist': self.specialist.id,
                     'service': self.service.id}

    def test_POST_method_create_order_not_logged_user(self):
        """Only a logged user can create an order."""
        self.client.force_authenticate(user=None)
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 401)

    def test_POST_method_create_order_logged_user(self):
        """A logged user should be able to create an order"""
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 201)

    def test_POST_method_create_order_service_not_exist_for_specialist(self):
        """Service should exist for specialist."""
        self.position.specialist.remove(self.specialist)
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 400)

    def test_POST_method_create_order_wrong_service_empty(self):
        """Service of the order should not be empty."""
        self.data["service"] = ""
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 400)

    def test_POST_method_create_order_wrong_specialist_empty(self):
        """Specialist of the order should not be empty."""
        self.data["specialist"] = ""
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 400)

    def test_POST_method_create_order_cant_specialist_to_himself(self):
        """Specialist should not be able to create order for himself."""
        self.client.force_authenticate(user=self.specialist)
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 400)
