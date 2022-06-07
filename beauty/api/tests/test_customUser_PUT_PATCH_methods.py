"""This module is for testing CustomUserDetailRUDView.

Tests for CustomUserDetailRUDView:
- SetUp method adds needed data for tests;
- User must be authorized;
- User can not change other user info;
- Valid PATCH request;
- PATCH with dublicated fields;
- PUT valid;
- PUT dublicate email;
- PUT empty data;
- PATCH empty data;
"""

import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.models import CustomUser
from api.views_api import CustomUserDetailRUDView
from api.serializers.customuser_serializers import CustomUserDetailSerializer
from .factories import CustomUserFactory


class TestCustomUserDetailRUDView(TestCase):
    """TestCase to test CustomUserDetailRUDView."""

    def setUp(self):
        """Create customer."""
        self.customer = CustomUserFactory.create()
        self.customer_testing = CustomUserFactory.create()

        self.serializer = CustomUserDetailSerializer
        self.queryset = CustomUser.objects.all()
        self.view = CustomUserDetailRUDView.as_view()
        self.client = APIClient()

        self.client.force_authenticate(user=self.customer_testing)
        self.url = "api:user-detail"
        self.pk = self.customer_testing.id

    def test_custom_user_no_authorized(self):
        """PATCH requests with authenticate None."""
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps({"first_name": "Angle"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_custom_user_patch_other(self):
        """PATCH requests to other id."""
        response = self.client.put(
            path=reverse(
                self.url,
                kwargs={"pk": self.customer.id},
            ),
            data=json.dumps({"first_name": "Angle"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_custom_user_patch_valid(self):
        """PATCH requests with valid data should change data."""
        response = self.client.patch(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps({"first_name": "Angle"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_custom_user_patch_dublicate(self):
        """PATCH requests with dublicate email shouldn't change it."""
        response = self.client.patch(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps({"email": self.customer.email}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_custom_user_put_valid(self):
        """PUT requests with valid data should change data."""
        self.customer_put = CustomUserFactory.build()
        self.data = {
            "email": self.customer_put.email,
            "first_name": self.customer_put.first_name,
            "groups": [],
            "phone_number": self.customer_put.phone_number.as_e164,
            "password": "choko5959",
            "confirm_password": "choko5959",
        }
        response = self.client.put(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_custom_user_put_invalid(self):
        """PUT requests with invalid data shouldn't change data."""
        self.customer_put = CustomUserFactory.build()
        self.data = {
            "email": self.customer.email,
            "first_name": self.customer_put.first_name,
            "groups": [],
            "phone_number": self.customer_put.phone_number.as_e164,
            "password": "choko5959",
            "confirm_password": "choko5959",
        }
        response = self.client.put(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps(self.data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_custom_user_put_empty(self):
        """PUT requests with empty data shouldn't work."""
        response = self.client.put(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_custom_user_patch_empty(self):
        """PATCH requests with empty data should work."""
        response = self.client.patch(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)
