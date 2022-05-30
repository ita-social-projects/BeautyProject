"""The module includes tests for CustomUser serializers."""

import json
from django.test import TestCase

from api.models import CustomUser
from api.serializers.customuser_serializers import (CustomUserSerializer,
                                                    CustomUserDetailSerializer,
                                                    PasswordsValidation)
from rest_framework.test import APIRequestFactory
from rest_framework.serializers import ValidationError


factory = APIRequestFactory()

request = factory.get('/')


class CustomUserSerializerTestCase(TestCase):
    """Tests for CustomUser serializers."""

    fixtures = ['customuser_serializer_test/customusers_test_data.json', ]

    def setUp(self):
        """Set up data for tests."""
        self.serializer = CustomUserSerializer
        self.detail_serializer = CustomUserDetailSerializer
        self.queryset = CustomUser.objects.all()

    def test_relative_hyperlinks(self):
        """Serialize all users with relative hyperlinks using
        CustomUserSerializer.
        """
        with open('api/fixtures/customuser_serializer_test/'
                  'relative_hyperlinks_expected_data.json') as f:
            expected = json.load(f)
            serializer = self.serializer(
                self.queryset, many=True,
                context={'request': None}
            )
            self.assertEqual(serializer.data, expected)

    def test_reverse_many_to_many_retrieve(self):
        """Serialize all users with reverse many to many retrieve using
        CustomUserSerializer.
        """
        with open('api/fixtures/customuser_serializer_test/'
                  'retrieve_create_expected_data.json') as f:
            expected = json.load(f)
            serializer = self.serializer(
                self.queryset, many=True,
                context={'request': request}
            )
            with self.assertNumQueries(16):
                self.assertEqual(serializer.data, expected)

    def test_deserialize_create_user(self):
        """Deserializing a data and creating a new user."""
        data = {"url": "http://testserver/api/v1/user/6/",
                "id": 6,
                "email": "m6@com.ua",
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
                "confirm_password": "0967478911m"}
        serializer = self.serializer(
            data=data,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj = serializer.save()
        saved_obj = self.queryset.get(id=6)
        data['avatar'] = 'http://testserver/media/default_avatar.jpeg'
        data.pop('password'),
        data.pop('confirm_password')
        self.assertEqual(saved_obj, obj)
        self.assertEqual(serializer.data, data)
        self.assertEqual(obj.email, "m6@com.ua")

        # Ensure target 6 is added, and everything else is as expected
        with open('api/fixtures/customuser_serializer_test/'
                  'retrieve_create_expected_data.json') as f:
            expected = json.load(f)
            expected.append(data)
            serializer = self.serializer(
                self.queryset, many=True,
                context={'request': request}
            )
            self.assertEqual(serializer.data, expected)

    def test_deserialize_update_user(self):
        """Deserializing a data and updating a user data."""
        data = {'first_name': 'Specialist_1_1', 'email': 'test@com.ua'}
        instance = self.queryset[0]
        serializer = self.detail_serializer(
            instance=instance, data=data,
            partial=True,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()
        self.assertEqual(serializer.data['first_name'], data['first_name'])
        self.assertEqual(serializer.data['email'], data['email'])


class PasswordsValidationTest(TestCase):
    """Tests for checking password and password confirmation when user
     creating user or updating user data.
     """

    valid_data = {"password": "0967478911m", "confirm_password": "0967478911m"}
    invalid_data = {"password": "0967478911m", "confirm_password": "096747891"}
    null_data_one = {"password": "", "confirm_password": "096747891"}
    null_data_two = {"password": "0967478911m", "confirm_password": ""}

    def setUp(self):
        """Set up data for tests."""
        self.validator = PasswordsValidation()

    def test_valid_data(self):
        """Checking valid data."""
        data = self.validator.validate(self.valid_data)
        self.assertEqual(data, self.valid_data)

    def test_invalid_data(self):
        """Checking invalid data."""
        with self.assertRaises(ValidationError) as ex:
            self.validator.validate(self.invalid_data)
        self.assertEqual(
            {"password": "Password confirmation does not match."},
            ex.exception.args[0]
        )

    def test_password_null(self):
        """Checking when password or password confirmation is null."""
        with self.assertRaises(ValidationError) as ex:
            self.validator.validate(self.null_data_one)
            self.validator.validate(self.null_data_two)
        self.assertEqual(
            {'confirm_password': 'Didn`t enter the password confirmation.'},
            ex.exception.args[0]
        )
