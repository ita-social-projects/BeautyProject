"""This module is for testing order's serializers.

Tests for OrderSerializer:
- Set up data for tests;
- Check serializer with valid data;
- Check serializer with invalid data;
- Check serializer with invalid data type;
- Check serializer with partial validation;
- Check serializer without data;
- Check serializer with data equal None;
- Check serializer when a chosen specialist does not have chosen service;
- Check serializer when customer and specialist are the same person.
"""

import pytz
from django.test import TestCase
from rest_framework.exceptions import ErrorDetail, ValidationError

from api.serializers.order_serializers import OrderSerializer
from .factories import *

CET = pytz.timezone("Europe/Kiev")


class TestOrderSerializer(TestCase):
    """Tests for OrderSerializer."""

    def setUp(self):
        """Set up data for tests."""
        self.Serializer = OrderSerializer

        self.groups = GroupFactory.groups_for_test()
        self.specialist = CustomUserFactory(first_name="UserSpecialist")
        self.customer = CustomUserFactory(first_name="UserCustomer")
        self.position = PositionFactory(name="Position_1")
        self.service = ServiceFactory(name="Service_1", position=self.position)

        self.groups.specialist.user_set.add(self.specialist)
        self.groups.customer.user_set.add(self.customer)
        self.position.specialist.add(self.specialist)

    def test_valid_serializer(self):
        """Check serializer with valid data."""
        valid_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                      'specialist': self.specialist.id,
                      'service': self.service.id}

        ecxpect_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                        'specialist': self.specialist,
                        'service': self.service}

        serializer = self.Serializer(data=valid_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data, ecxpect_data)
        self.assertEqual(serializer.errors, {})
        order = serializer.save(customer=self.customer)
        self.assertEqual(order.status, 0)
        self.assertEqual(order.customer, self.customer)

    def test_invalid_serializer(self):
        """Check serializer with invalid data."""
        invalid_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                        'specialist': self.specialist.id}

        serializer = self.Serializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.data, invalid_data)
        self.assertEqual(serializer.errors, {
            'service': [ErrorDetail(string='This field is required.', code='required')]})

    def test_invalid_datatype(self):
        """Check serializer with invalid data type."""
        invalid_data = [{'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                         'specialist': self.specialist.id,
                         'service': self.service}]

        serializer = self.Serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.data, {})
        self.assertEqual(serializer.errors, {'non_field_errors': [ErrorDetail(
            string='Invalid data. Expected a dictionary, but got list.', code='invalid')]
        })

    def test_partial_validation(self):
        """Check serializer with partial validation."""
        invalid_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                        'specialist': self.specialist.id}

        ecxpect_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                        'specialist': self.specialist}

        serializer = self.Serializer(data=invalid_data, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, ecxpect_data)
        self.assertEqual(serializer.errors, {})

    def test_empty_serializer(self):
        """Check serializer without data."""
        serializer = self.Serializer()
        self.assertEqual(serializer.data, {'specialist': None, 'service': None, 'start_time': None})

    def test_validate_none_data(self):
        """Check serializer with data equal None."""
        data = None
        serializer = self.Serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {'non_field_errors': ['No data provided']})

    def test_specialist_service(self):
        """Check serializer when a chosen specialist does not have chosen service."""
        valid_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                      'specialist': self.specialist.id,
                      'service': self.service.id}

        self.position.specialist.remove(self.specialist)

        serializer = self.Serializer(data=valid_data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})

        with self.assertRaises(ValidationError) as ex:
            self.assertTrue(serializer.is_valid())
            serializer.save(customer=self.customer)
        self.assertEqual(
            {'help_text': 'Specialist has such services [].',
             'service': 'Specialist does not have such service.'}, ex.exception.args[0]
        )

    def test_specialist_is_customer(self):
        """Check serializer when customer and specialist are the same person."""
        valid_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                      'specialist': self.specialist.id,
                      'service': self.service.id}

        serializer = self.Serializer(data=valid_data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})

        with self.assertRaises(ValidationError) as ex:
            self.assertTrue(serializer.is_valid())
            serializer.save(customer=self.specialist)
        self.assertEqual(
            {'users': 'Customer and specialist are the same person!'}, ex.exception.args[0]
        )
