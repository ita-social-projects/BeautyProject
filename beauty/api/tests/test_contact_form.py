"""This module is for testing website support functionality.

It tests ContactFormView.

Tests:
    *   Test view with valid data
    *   Test view with invalid data
    *   Test view with empty data

"""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient


class ContactFormTest(TestCase):
    """Tests for website support functionality."""

    def setUp(self) -> None:
        """Sets up instances for tests."""
        self.client = APIClient()

        self.data = {
            "name": "Service_2",
            "email": "test@gmail.com",
            "message": "test",
        }

        self.invalid_data = {
            "name": "Service_2" * 30,
            "email": "test@gmail.com",
            "message": "test",
        }

    def test_valid_data(self) -> None:
        """Testing post method with valid data."""
        response = self.client.post(
            path=reverse("api:contact-form"),
            data=self.data,
        )
        self.assertEqual(response.status_code, 302)

    def test_invalid_data(self) -> None:
        """Testing post method with invalid data."""
        response = self.client.post(
            path=reverse("api:contact-form"),
            data=self.invalid_data,
        )
        self.assertEqual(response.status_code, 400)

    def test_empty_data(self) -> None:
        """Testing post method with empty data."""
        response = self.client.post(
            path=reverse("api:contact-form"),
            data={},
        )
        self.assertEqual(response.status_code, 400)
