"""This module is for testing filtering algorithms for services.

Tests:
    *   Test searching by name of service
    *   Test filtering by name of service
    *   Test ordering by service price descending
    *   Test ordering by service price ascending
"""


from django.test import TestCase
from django.urls import reverse

from api.models import Service

from rest_framework.test import APIClient

from .factories import PositionFactory

from datetime import timedelta


class ServiceFilterTest(TestCase):
    """Tests for Service filtering, searching and ordering algorithms."""

    def setUp(self):
        """Sets up instances for tests."""
        self.client = APIClient()

        self.position = PositionFactory.create()

        self.service1 = Service.objects.create(name="service_1", price=10,
                                               duration=timedelta(minutes=30),
                                               position=self.position)
        self.service2 = Service.objects.create(name="service_2", price=20,
                                               duration=timedelta(minutes=40),
                                               position=self.position)
        self.service3 = Service.objects.create(name="service_3", price=50,
                                               duration=timedelta(minutes=45),
                                               position=self.position)

    def test_get_search(self):
        """Searching by name of service."""
        url = reverse("api:service-list-create")
        response = self.client.get(url, data={"search": "service"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)

    def test_get_filter(self):
        """Filtering by name of service."""
        url = reverse("api:service-list-create")
        response = self.client.get(url, data={"name": "service_2"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_get_ordering_desc(self):
        """Ordering by service price descending."""
        url = reverse("api:service-list-create")
        response = self.client.get(url, data={"ordering": "-price"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], 3)

    def test_get_ordering_asc(self):
        """Ordering by service price ascending."""
        url = reverse("api:service-list-create")
        response = self.client.get(url, data={"ordering": "price"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], 1)
