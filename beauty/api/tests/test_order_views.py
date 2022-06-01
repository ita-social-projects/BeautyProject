"""This module is for testing order"s views.

Tests for OrderListCreateView:
- SetUp method adds needed info for tests;
- Only a logged user can create an order;
- A logged user should be able to create an order;
- Service should exist for specialist;
- Service of the order should not be empty;
- Specialist of the order should not be empty;
- Specialist should not be able to create order for himself.

Tests for OrderApprovingView:
- SetUp method adds needed info for tests;
- The specialist is redirected to the order detail page if he approved the order;
- The specialist is redirected to the own page if he declined the order;
- The specialist is redirected to the own page if the order token expired;
- The user is redirected to the order specialist detail page if he is not logged.
"""

import pytz
from django.utils import timezone
from django.test import TestCase
from djoser.utils import encode_uid
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api.serializers.order_serializers import OrderSerializer
from api.views import (OrderListCreateView,
                       OrderApprovingTokenGenerator)
from .factories import (GroupFactory,
                        CustomUserFactory,
                        PositionFactory,
                        ServiceFactory,
                        OrderFactory)


CET = pytz.timezone("Europe/Kiev")


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

        self.data = {"start_time": timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                     "specialist": self.specialist.id,
                     "service": self.service.id}

    def test_post_method_create_order_not_logged_user(self):
        """Only a logged user can create an order."""
        self.client.force_authenticate(user=None)
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 401)

    def test_post_method_create_order_logged_user(self):
        """A logged user should be able to create an order."""
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 201)

    def test_post_method_create_order_service_not_exist_for_specialist(self):
        """Service should exist for specialist."""
        self.position.specialist.remove(self.specialist)
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_order_wrong_service_empty(self):
        """Service of the order should not be empty."""
        self.data["service"] = ""
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_order_wrong_specialist_empty(self):
        """Specialist of the order should not be empty."""
        self.data["specialist"] = ""
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_order_cant_specialist_to_himself(self):
        """Specialist should not be able to create order for himself."""
        self.client.force_authenticate(user=self.specialist)
        response = self.client.post(path=reverse("api:order-list-create"), data=self.data)
        self.assertEqual(response.status_code, 400)


class TestOrderApprovingView(TestCase):
    """This class represents a Test case and has all the tests for OrderApprovingView."""

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.Serializer = OrderSerializer
        self.client = APIClient()

        self.specialist = CustomUserFactory(first_name="UserSpecialist")
        self.customer = CustomUserFactory(first_name="UserCustomer")
        self.service = ServiceFactory(name="Service_1")

        self.client.force_authenticate(user=self.customer)

        self.order = OrderFactory(specialist=self.specialist,
                                  customer=self.customer,
                                  service=self.service)

        self.token = OrderApprovingTokenGenerator().make_token(self.order)
        self.status_approved = encode_uid("approved")
        self.status_declined = encode_uid("declined")
        self.url_kwargs = {"uid": encode_uid(self.order.pk),
                           "token": self.token,
                           "status": self.status_approved}

    def test_get_method_get_status_approved(self):
        """The specialist is redirected to the order detail page if he approved the order."""
        response = self.client.get(path=reverse("api:order-approving", kwargs=self.url_kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("api:user-order-detail",
                                               kwargs={"user": self.order.specialist.id,
                                                       "pk": self.order.id}))

    def test_get_method_get_status_declined(self):
        """The specialist is redirected to the own page if he declined the order."""
        self.url_kwargs["status"] = self.status_declined
        response = self.client.get(path=reverse("api:order-approving", kwargs=self.url_kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("api:user-detail",
                                               args=[self.order.specialist.id]))

    def test_get_method_get_status_invalid_token(self):
        """The specialist is redirected to the own page if the order token expired."""
        self.url_kwargs["token"] = "invalid"
        response = self.client.get(path=reverse("api:order-approving", kwargs=self.url_kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("api:user-detail",
                                               args=[self.order.specialist.id]))

    def test_get_method_not_logged_user_redirect_to_specialist(self):
        """The user is redirected to the order specialist detail page if he is not logged."""
        self.client.force_authenticate(user=None)
        response = self.client.get(path=reverse("api:order-approving", kwargs=self.url_kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("api:user-order-detail",
                                               kwargs={"user": self.order.specialist.id,
                                                       "pk": self.order.id}))
