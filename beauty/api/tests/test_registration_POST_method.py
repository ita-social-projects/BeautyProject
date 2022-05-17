import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import unittest

from api.serializers.serializers_customuser import (
                                                    CustomUserSerializer,
                                                    CustomUserDetailSerializer
                                                    )
from api.models import CustomUser
from api.views import CustomUserListCreateView


class TestCustomUserListCreateView(TestCase):
    def setUp(self):
        """
        Create 3 CustomUser instances.
        """
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
                    "groups": ['Specialist', ],
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
                    "phone_number": "+380967470017",
                    "bio": "Specialist_6",
                    "rating": 0,
                    "is_active": True,
                    "groups": ['Specialist', ],
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
                    "groups": ['Specialist', ],
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
        

    def test_get_custom_user_list_create_view(self):
        """
        GET requests to ListCreateAPIView should return list of objects.
        """
        response = self.client.get('http://127.0.0.1:8000/api/v1/user/')
        assert response.status_code == status.HTTP_200_OK


    def test_post_custom_user_list_create_view(self):
        """
        POST requests to ListCreateAPIView should create a new object.
        """
        response = self.client.post('http://127.0.0.1:8000/api/v1/user/', data=self.items[0])
        assert response.status_code == status.HTTP_201_CREATED

    def test_post_cannot_set_id(self):
        """
        POST requests to create a new object should not be able to set the id.
        """
        pass
