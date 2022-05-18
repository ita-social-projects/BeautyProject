"""Module contains test for generic post method for user registration"""

from django.test import TestCase
from rest_framework.test import APIClient

from api.serializers.serializers_customuser import (
                                                    CustomUserSerializer,
                                                    CustomUserDetailSerializer
                                                    )
from api.models import CustomUser
from api.views import CustomUserListCreateView


class TestCustomUserListCreateView(TestCase):
    """TestCase to test POST method, which is generics.ListCreateView"""

    def setUp(self):
        """
        Create 3 CustomUser instances.
        """
        # List of 3 dicts, where each dict contains CustomUser data
        # 1 element correct,
        # 2 element with invalid phone,
        # 3 with invalid confirm_password
        # -1 and -2 elements are valid,
        # and used for creating objects for testing GET method
        self.items = [
                {
                    "url": "http://testserver/api/v1/user/10/",
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
                },
                {
                    "url": "http://testserver/api/v1/user/11/",
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
                },
                {
                    "url": "http://testserver/api/v1/user/12/",
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
                },
                {
                    "url": "http://testserver/api/v1/user/10/",
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
                },
                {
                    "url": "http://testserver/api/v1/user/10/",
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
        ]
        self.serializer = CustomUserSerializer
        self.detail_serializer = CustomUserDetailSerializer
        self.queryset = CustomUser.objects.all()
        self.view = CustomUserListCreateView.as_view()
        self.client = APIClient()

        # Needed for GET method testing
        self.client.post(
                        'http://127.0.0.1:8000/api/v1/user/',
                        data=self.items[-1]
                        )
        self.client.post(
                        'http://127.0.0.1:8000/api/v1/user/',
                        data=self.items[-2]
                        )


    def test_get_custom_user_list_create_view(self):
        """
        GET requests to ListCreateAPIView should return list of objects.
        """
        # self.client.generic needed for getting data from GET method
        resp = self.client.generic(
                                    method="GET",
                                    path="http://127.0.0.1:8000/api/v1/user/"
                                    )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_post_custom_user_list_create_view(self):
        """
        POST requests to ListCreateAPIView should create a new object.
        """
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/user/',
                                    data=self.items[0]
                                    )
        self.assertEqual(response.status_code, 201)

    def test_post_dublicate_custom_user(self):
        """
        POST requests to ListCreateAPIView
        should not create a new object if same object already exists.
        """
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/user/',
                                    data=self.items[-1]
                                    )
        self.assertEqual(response.status_code, 400)

    def test_post_invalid_phone(self):
        """
        POST requests to ListCreateAPIView with phone number which doesn't match regex
        should not create a new object.
        """
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/user/',
                                    data=self.items[1]
                                    )
        self.assertEqual(response.status_code, 400)

    def test_post_invalid_confirm_password(self):
        """
        POST requests to ListCreateAPIView
        with different password and confirm_password should not create a new object.
        """
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/user/',
                                    data=self.items[2]
                                    )
        self.assertEqual(response.status_code, 400)

    def test_post_empty_data(self):
        """
        POST requests to ListCreateAPIView with empty data shoul not create a new object.
        """
        response = self.client.post(
                                    'http://127.0.0.1:8000/api/v1/user/',
                                    data={}
                                    )
        self.assertEqual(response.status_code, 400)
