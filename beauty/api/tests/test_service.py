"""This module is for testing GET, POST, PUT, DELETE methods that is used to create or edit service.

It tests ServiceListCreateView and ServiceUpdateView.

Tests:
    *   Test that view displays all services
    *   Test that user can't create service without owner access
    *   Test that user can create service with owner access
    *   Test that service can't be created with empty data
    *   Test that service can't be created with invalid data
    *   Test that user can edit service without owner access
    *   Test that user can edit service with owner access
    *   Test that user can't delete service without owner access
    *   Test that user can delete service with owner access

"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient

from faker import Faker

from .factories import (
    CustomUserFactory,
    PositionFactory,
    GroupFactory,
    ServiceFactory,
)

User = get_user_model()
faker = Faker()


class ServiceModelTest(TestCase):
    """Tests for basic Service model behavior and its methods."""

    def setUp(self) -> None:
        """Sets up instances for tests.

        Preparing owner, position, services and other data for the tests.
        """
        self.client = APIClient()

        self.groups = GroupFactory.groups_for_test()

        self.position = PositionFactory.create()

        self.service1 = ServiceFactory.create()
        self.service2 = ServiceFactory.create()

        self.owner = CustomUserFactory.create()
        self.groups.owner.user_set.add(self.owner)

        self.data = {
            "position": 1,
            "name": "Service_2",
            "price": "33.00",
            "description": "",
            "duration": 46,
        }
        self.invalid_data = {
            "position": 1,
            "name": "Service_2" * 50,
            "price": "33.00",
            "description": "",
            "duration": 46,
        }

    def test_list_of_services(self) -> None:
        """Tests if view gives all services."""
        response = self.client.get(
            path=reverse("api:service-list-create"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_service_post_no_permission(self) -> None:
        """Test if user can create service without owner permission."""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            path=reverse("api:service-list-create"),
            data=self.data,
        )
        self.assertEqual(response.status_code, 401)

    def test_service_post_with_permission(self) -> None:
        """Test if user can create service with owner permission."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            path=reverse("api:service-list-create"),
            data=self.data,
        )
        self.assertEqual(response.status_code, 201)

    def test_service_post_with_invalid_data(self) -> None:
        """Test if user can create service with invalid data."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            path=reverse("api:service-list-create"),
            data=self.invalid_data,
        )
        self.assertEqual(response.status_code, 400)

    def test_service_post_with_empty_data(self) -> None:
        """Test if user can create service with invalid data."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            path=reverse("api:service-list-create"),
            data={},
        )
        self.assertEqual(response.status_code, 400)

    def test_service_put_method_not_owner(self) -> None:
        """Test if user can update service without owner permission."""
        self.client.force_authenticate(user=None)
        response = self.client.put(
            path=reverse("api:service-detail", kwargs={"pk": self.service1.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 401)

    def test_service_put_method_owner(self) -> None:
        """Test if user can update service with owner permission."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(
            path=reverse("api:service-detail", kwargs={"pk": self.service1.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 200)

    def test_service_delete_not_owner(self) -> None:
        """Test if user can delete service with owner permission."""
        self.client.force_authenticate(user=None)
        response = self.client.delete(
            path=reverse("api:service-detail", kwargs={"pk": self.service1.id}),
        )
        self.assertEqual(response.status_code, 401)

    def test_service_delete_owner(self) -> None:
        """Test if user can delete service with owner permission."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(
            path=reverse("api:service-detail", kwargs={"pk": self.service1.id}),
        )
        self.assertEqual(response.status_code, 204)
