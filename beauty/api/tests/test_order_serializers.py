"""This module is for testing order"s serializers.

Tests for OrderSerializer:
- This method adds needed info for tests;
- Check serializer with valid data;
- Check serializer with invalid data;
- Check serializer with invalid start_time field;
- Check serializer with invalid data type;
- Check serializer with partial validation;
- Check serializer without data;
- Check serializer with data equal None;
- Check serializer when a chosen specialist does not have chosen service;
- Check serializer when customer and specialist are the same person.
"""

import pytz
from django.utils import timezone
from django.test import TestCase
from rest_framework.exceptions import ErrorDetail, ValidationError

from api.serializers.order_serializers import OrderSerializer
from api.tests.factories import (GroupFactory,
                                 CustomUserFactory,
                                 PositionFactory,


CET = pytz.timezone("Europe/Kiev")


class TestOrderSerializer(TestCase):
    """This class represents a Test case and has all the tests for OrderSerializer."""

    def setUp(self):
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
        self.factory = APIRequestFactory()
        self.request = self.factory.get("/")
        self.request.user = self.customer
        self.start_time = timezone.datetime.now(tz=CET) + timezone.timedelta(days=2)

    def test_valid_serializer(self):
        """Check serializer with valid data."""
        valid_data = {"start_time": self.start_time,
                      "specialist": self.specialist.id,
                      "service": self.service.id}

        ecxpect_data = {"start_time": self.start_time,
                        "specialist": self.specialist,
                        "service": self.service}

        serializer = self.Serializer(data=valid_data, context={"request": self.request})
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data, ecxpect_data)
        self.assertEqual(serializer.errors, {})
        order = serializer.save(customer=self.customer)
        self.assertEqual(order.status, 0)
        self.assertEqual(order.customer, self.customer)

    def test_invalid_serializer(self):
        """Check serializer with invalid data."""
        invalid_data = {"start_time": self.start_time,
                        "specialist": self.specialist.id}

        serializer = self.Serializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.data, invalid_data)
        self.assertEqual(serializer.errors, {
            "service": [ErrorDetail(string="This field is required.", code="required")]})

    def test_invalid_start_time(self):
        """Check serializer with invalid start_time field."""
        invalid_data = {"start_time": self.start_time - timezone.timedelta(days=30),
                        "specialist": self.specialist.id,
                        "service": self.service.id}

        serializer = self.Serializer(data=invalid_data, context={"request": self.request})
        serializer.is_valid()

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.data, invalid_data)
        self.assertEqual(serializer.errors, {
            "start_time": [ErrorDetail(string="The start time should be more as now.",
                                       code="invalid")],
        })

    def test_invalid_datatype(self):
        """Check serializer with invalid data type."""
        invalid_data = [{"start_time": self.start_time,
                         "specialist": self.specialist.id,
                         "service": self.service}]

        serializer = self.Serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.data, {})
        self.assertEqual(serializer.errors, {"non_field_errors": [ErrorDetail(
            string="Invalid data. Expected a dictionary, but got list.", code="invalid")],
        })

    def test_partial_validation(self):
        """Check serializer with partial validation."""
        invalid_data = {"start_time": self.start_time,
                        "specialist": self.specialist.id,
                        "service": self.service.id}

        ecxpect_data = {"start_time": self.start_time,
                        "specialist": self.specialist,
                        "service": self.service}

        serializer = self.Serializer(data=invalid_data, partial=True,
                                     context={"request": self.request})

        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data, ecxpect_data)
        self.assertEqual(serializer.errors, {})

    def test_empty_serializer(self):
        """Check serializer without data."""
        serializer = self.Serializer()
        self.assertEqual(serializer.data, {"specialist": None, "service": None,
                                           "start_time": None, "note": ""})

    def test_validate_none_data(self):
        """Check serializer with data equal None."""
        data = None
        serializer = self.Serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {"non_field_errors": ["No data provided"]})

    def test_specialist_service(self):
        """Check serializer when a chosen specialist does not have chosen service."""
        valid_data = {"start_time": self.start_time,
                      "specialist": self.specialist.id,
                      "service": self.service.id}

        self.position.specialist.remove(self.specialist)

        serializer = self.Serializer(data=valid_data, context={"request": self.request})

        with self.assertRaises(ValidationError) as ex:
            self.assertTrue(serializer.is_valid(raise_exception=True))
            serializer.save(customer=self.customer)

        self.assertEqual(
            {"service": {"message": ErrorDetail(
                string=f"Specialist {self.specialist.get_full_name()} does not have "
                       f"{self.service.name} service.",
                code="invalid"), "help_text": ErrorDetail(
                string=f"Specialist {self.specialist.get_full_name()} has such services [].",
                code="invalid")}},
            ex.exception.args[0],
        )

    def test_specialist_is_customer(self):
        """Check serializer when customer and specialist are the same person."""
        valid_data = {"start_time": self.start_time,
                      "specialist": self.specialist.id,
                      "service": self.service.id}
        self.request.user = self.specialist
        serializer = self.Serializer(data=valid_data, context={"request": self.request})

        with self.assertRaises(ValidationError) as ex:
            self.assertTrue(serializer.is_valid(raise_exception=True))
            serializer.save()
        self.assertEqual(
            {"users": [
                ErrorDetail(string="Customer and specialist are the same person!", code="invalid"),
            ]}, ex.exception.args[0],
        )
