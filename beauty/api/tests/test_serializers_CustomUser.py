"""The module includes tests for CustomUser serializers."""

import json
from django.test import TestCase
from api.models import CustomUser
from api.serializers.serializers_customuser import (CustomUserSerializer,
                                                    CustomUserDetailSerializer,
                                                    PasswordsValidation)
from rest_framework.test import APIRequestFactory
from rest_framework.serializers import ValidationError

factory = APIRequestFactory()

request = factory.get('/')


class CustomUserSerializerTestCase(TestCase):
    """Tests for CustomUser serializers."""

    fixtures = ['customuser_serializer_test/customusers_test_data.json',
                'customuser_serializer_test/groups_test_data.json',
                'customuser_serializer_test/orders_test_data.json']

    def setUp(self):
        self.serializer = CustomUserSerializer
        self.detail_serializer = CustomUserDetailSerializer
        self.queryset = CustomUser.objects.all()

    def test_relative_hyperlinks(self):
        with open('api/fixtures/customuser_serializer_test/'
                  'relative_hyperlinks_expected_data.json') as f:
            expected = json.load(f)
            serializer = self.serializer(
                self.queryset, many=True,
                context={'request': None}
            )
            with self.assertNumQueries(13):
                self.assertEqual(serializer.data, expected)

    def test_reverse_many_to_many_retrieve(self):
        with open('api/fixtures/customuser_serializer_test/'
                  'retrieve_create_expected_data.json') as f:
            expected = json.load(f)
            serializer = self.serializer(
                self.queryset, many=True,
                context={'request': request}
            )
            with self.assertNumQueries(13):
                self.assertEqual(serializer.data, expected)

    def test_reverse_many_to_many_create(self):
        data = {"url": "http://testserver/api/v1/user/5/",
                "id": 5,
                "email": "m5@com.ua",
                "first_name": "Specialist_5",
                "patronymic": "PSpecialist_5",
                "last_name": "LSpecialist_5",
                "phone_number": "+380967470006",
                "bio": "Specialist_5",
                "rating": 0,
                "avatar": None,
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
        data.pop('password'),
        data.pop('confirm_password')
        self.assertEqual(serializer.data, data)
        self.assertEqual(obj.email, "m5@com.ua")

        # Ensure target 4 is added, and everything else is as expected
        with open('api/fixtures/customuser_serializer_test/'
                  'retrieve_create_expected_data.json') as f:
            expected = json.load(f)
            expected.append(data)
            serializer = self.serializer(
                self.queryset, many=True,
                context={'request': request}
            )
            self.assertEqual(serializer.data, expected)

    def test_reverse_many_to_many_update(self):
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
    valid_data = {"password": "0967478911m", "confirm_password": "0967478911m"}
    invalid_data = {"password": "0967478911m", "confirm_password": "096747891"}
    null_data_one = {"password": "", "confirm_password": "096747891"}
    null_data_two = {"password": "0967478911m", "confirm_password": ""}

    def setUp(self):
        self.validator = PasswordsValidation()

    def test_valid_data(self):
        data = self.validator.validate(self.valid_data)
        self.assertEqual(data, self.valid_data)

    def test_invalid_data(self):
        with self.assertRaises(ValidationError) as ex:
            self.validator.validate(self.invalid_data)
        self.assertEqual(
            {"password": "Password confirmation does not match."},
            ex.exception.args[0]
        )

    def test_password_null(self):
        with self.assertRaises(ValidationError) as ex:
            self.validator.validate(self.null_data_one)
            self.validator.validate(self.null_data_two)
        self.assertEqual(
            {'confirm_password': 'Didn`t enter the password confirmation.'},
            ex.exception.args[0]
        )
