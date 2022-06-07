"""This module is for testing registration POST view.

Tests for CustomUserListCreateView:
- SetUp method adds needed info for tests;
- Get 2 created and posted customers;
- Pass a valid customer data;
- Dublicates email are not allowed;
- Phone number must match the regex;
- Password and confirmation password must match;
- Customer isn't allowed to post empty data.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.serializers.customuser_serializers import CustomUserSerializer

from api.models import CustomUser
from api.views_api import CustomUserListCreateView
from .factories import CustomUserFactory


class TestCustomUserListCreateView(TestCase):
    """TestCase to test POST method, which is generics.ListCreateView."""

    def setUp(self):
        """Create 3 CustomUser instances."""
        # Dictionary needed for successfull POST method instead of factrories
        self.customer = {"email": "m613@com.ua",
                         "first_name": "Specialist_8",
                         "phone_number": "+380967470021",
                         "password": "0967478911m",
                         "confirm_password": "0967478911m",
                         }

        self.serializer = CustomUserSerializer
        self.queryset = CustomUser.objects.all()
        self.view = CustomUserListCreateView.as_view()
        self.client = APIClient()

    def test_get_custom_user_list_create_view(self):
        """GET requests to ListCreateAPIView should return list of objects."""
        self.customer_get = CustomUserFactory.create(first_name="Aha")
        resp = self.client.generic(method="GET",
                                   path=reverse("api:user-list-create"),
                                   )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_post_custom_user_list_create_view(self):
        """POST requests to ListCreateAPIView should create a new object."""
        response = self.client.post(path=reverse("api:user-list-create"),
                                    data=self.customer,
                                    )
        self.assertEqual(response.status_code, 201)

    def test_post_dublicate_email_custom_user(self):
        """POST requests to ListCreateAPIView.

        Should not create a new object if same object already exists.
        """
        self.dub = CustomUserFactory.create(email=self.customer["email"])
        response = self.client.post(path=reverse("api:user-list-create"),
                                    data=self.customer,
                                    )
        self.assertEqual(response.status_code, 400)

    def test_post_invalid_phone(self):
        """POST requests to ListCreateAPIView.

        Phone number which doesn't match regex
        should not create a new object.
        """
        self.customer["phone_number"] = "+38097111111"
        response = self.client.post(path=reverse("api:user-list-create"),
                                    data=self.customer,
                                    )
        self.assertEqual(response.status_code, 400)

    def test_post_invalid_confirm_password(self):
        """POST requests to ListCreateAPIView.

        with different password and confirm_password should not create a new object.
        """
        self.customer["confirm_password"] = "abracadabra"
        response = self.client.post(path=reverse("api:user-list-create"),
                                    data=self.customer,
                                    )
        self.assertEqual(response.status_code, 400)

    def test_post_empty_data(self):
        """POST requests to ListCreateAPIView with empty data shoul not create a new object."""
        response = self.client.post(path=reverse("api:user-list-create"),
                                    data={},
                                    )
        self.assertEqual(response.status_code, 400)
