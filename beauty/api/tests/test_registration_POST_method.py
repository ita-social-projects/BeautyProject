"""Module contains test for generic post method for user registration"""

from django.test import TestCase
from rest_framework.test import APIClient

from api.serializers.customuser_serializers import (
                                                    CustomUserSerializer,
                                                    CustomUserDetailSerializer
                                                    )
from api.models import CustomUser
from api.views import CustomUserListCreateView


class TestCustomUserListCreateView(TestCase):
    """TestCase to test POST method, which is generics.ListCreateView"""

    def setUp(self):
        """Create 3 CustomUser instances."""

        self.valid_CustomUser = {
                    "url": "http://testserver/api/v1/users/10/",
                    "id": 10,
                    "email": "m61@com.ua",
                    "first_name": "Specialist_6",
                    "patronymic": "PSpecialist_6",
                    "last_name": "LSpecialist_6",
                    "phone_number": "+380967470016",
                    "bio": "Specialist_6",
                    "rating": 0,
                    "is_active": True,
                    "groups": [],
                    'specialist_orders': [],
                    'customer_orders': [],
                    "password": "0967478911m",
                    "confirm_password": "0967478911m"
                    }

        self.invalid_phone = {
                    "url": "http://testserver/api/v1/users/11/",
                    "id": 11,
                    "email": "m62@com.ua",
                    "first_name": "Specialist_6",
                    "patronymic": "PSpecialist_6",
                    "last_name": "LSpecialist_6",
                    "phone_number": "+38096747001",
                    "bio": "Specialist_6",
                    "rating": 0,
                    "is_active": True,
                    "groups": [],
                    'specialist_orders': [],
                    'customer_orders': [],
                    "password": "0967478911m",
                    "confirm_password": "0967478911m"
                    }

        self.invalid_confirmation_password = {
                    "url": "http://testserver/api/v1/users/12/",
                    "id": 12,
                    "email": "m63@com.ua",
                    "first_name": "Specialist_6",
                    "patronymic": "PSpecialist_6",
                    "last_name": "LSpecialist_6",
                    "phone_number": "+380967470018",
                    "bio": "Specialist_6",
                    "rating": 0,
                    "is_active": True,
                    "groups": [],
                    'specialist_orders': [],
                    'customer_orders': [],
                    "password": "0967478911m",
                    "confirm_password": "0967478911"
                    }

        self.valid_for_get_test_1 = {
                    "url": "http://testserver/api/v1/users/15/",
                    "id": 15,
                    "email": "m611@com.ua",
                    "first_name": "Specialist_6",
                    "patronymic": "PSpecialist_6",
                    "last_name": "LSpecialist_6",
                    "phone_number": "+380967470019",
                    "bio": "Specialist_6",
                    "rating": 0,
                    "is_active": True,
                    "groups": [],
                    'specialist_orders': [],
                    'customer_orders': [],
                    "password": "0967478911m",
                    "confirm_password": "0967478911m"
                    }
                    
        self.valid_for_get_test_2 = {
                    "url": "http://testserver/api/v1/users/16/",
                    "id": 16,
                    "email": "m6111@com.ua",
                    "first_name": "Specialist_6",
                    "patronymic": "PSpecialist_6",
                    "last_name": "LSpecialist_6",
                    "phone_number": "+380967470020",
                    "bio": "Specialist_6",
                    "rating": 0,
                    "is_active": True,
                    "groups": [],
                    'specialist_orders': [],
                    'customer_orders': [],
                    "password": "0967478911m",
                    "confirm_password": "0967478911m"
                }

        self.serializer = CustomUserSerializer
        self.detail_serializer = CustomUserDetailSerializer
        self.queryset = CustomUser.objects.all()
        self.view = CustomUserListCreateView.as_view()
        self.client = APIClient()

        # Needed for GET method testing
        self.client.post(
                        'http://127.0.0.1:8000/api/v1/users/',
                        data=self.valid_for_get_test_1
                        )
        self.client.post(
                        'http://127.0.0.1:8000/api/v1/users/',
                        data=self.valid_for_get_test_2
                        )


    def test_get_custom_user_list_create_view(self):
        """GET requests to ListCreateAPIView should return list of objects."""
        # self.client.generic needed for getting data from GET method
        resp = self.client.generic(
                                    method="GET",
                                    path="http://127.0.0.1:8000/api/v1/users/"
                                    )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_post_custom_user_list_create_view(self):
        """POST requests to ListCreateAPIView should create a new object."""
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/users/',
                                    data=self.valid_CustomUser
                                    )
        self.assertEqual(response.status_code, 201)

    def test_post_dublicate_custom_user(self):
        """POST requests to ListCreateAPIView
        should not create a new object if same object already exists.
        """
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/users/',
                                    data=self.valid_for_get_test_2
                                    )
        self.assertEqual(response.status_code, 400)

    def test_post_invalid_phone(self):
        """POST requests to ListCreateAPIView with phone number which doesn't match regex
        should not create a new object.
        """
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/users/',
                                    data=self.invalid_phone
                                    )
        self.assertEqual(response.status_code, 400)

    def test_post_invalid_confirm_password(self):
        """POST requests to ListCreateAPIView
        with different password and confirm_password should not create a new object.
        """
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/users/',
                                    data=self.invalid_confirmation_password
                                    )
        self.assertEqual(response.status_code, 400)

    def test_post_empty_data(self):
        """POST requests to ListCreateAPIView with empty data shoul not create a new object."""
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/users/',
                                    data={}
                                    )
        self.assertEqual(response.status_code, 400)