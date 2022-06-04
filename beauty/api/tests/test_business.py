"""Tests related to the Business model."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient

from faker import Faker

from .factories import (
    CustomUserFactory,
    BusinessFactory,
    PositionFactory,
    GroupFactory,
)
from beauty.utils import get_random_start_end_datetime

User = get_user_model()
faker = Faker()


class BusinessModelTest(TestCase):
    """Tests for basic Bussiness model behavior and its methods."""

    def setUp(self) -> None:
        """Sets up instances for tests.

        Preparing owner, two specialist, business and position for the tests
        """
        self.groups = GroupFactory.groups_for_test()

        self.owner = CustomUserFactory.create()
        self.groups.owner.user_set.add(self.owner)

        self.specialist1 = CustomUserFactory.create()
        self.specialist2 = CustomUserFactory.create()
        self.groups.specialist.user_set.add(self.specialist1)
        self.groups.specialist.user_set.add(self.specialist2)

        self.business = BusinessFactory.create()

        self.position = PositionFactory.create()
        self.position.specialist.add(self.specialist2)
        self.business.position_set.add(self.position)

    def test_create_position_method(self) -> None:
        """Test if create_position method.

        Creates new position and that this position belongs
        to a correct business
        """
        start_time, end_time = get_random_start_end_datetime()
        position = self.business.create_position(
            faker.word(), self.specialist1, start_time, end_time,
        )
        all_positions = self.business.position_set.all()

        self.assertIn(position, all_positions)
        self.assertEqual(len(all_positions), 2)

    def test_get_all_specialist_method(self) -> None:
        """Tests Business model get_all_specialist method.

        Checks if this method gives all specilaists who belong
        to current business
        """
        start_time, end_time = get_random_start_end_datetime()
        self.business.create_position(
            faker.word(), self.specialist1, start_time, end_time,
        )
        all_specialists = self.business.get_all_specialists()

        self.assertIn(self.specialist1, all_specialists)
        self.assertIn(self.specialist2, all_specialists)
        self.assertEqual(len(all_specialists), 2)


class BusinessListCreateViewTest(TestCase):
    """Tests for business' serilaizers and BusinessListCreateView."""

    def setUp(self) -> None:
        """Sets up.

        Creates client for authentification, creates 2 business, client,
        owner, valid and invalid data for business creation
        """
        self.client = APIClient()

        self.groups = GroupFactory.groups_for_test()

        self.business1 = BusinessFactory.create()
        self.business2 = BusinessFactory.create()

        self.customer = CustomUserFactory.create()
        self.owner = CustomUserFactory.create()
        self.groups.customer.user_set.add(self.customer)
        self.groups.owner.user_set.add(self.owner)

        self.valid_create_data = {
            "name": faker.word(), "business_type": faker.word(),
            "description": faker.text(),
        }
        self.invalid_create_data = {
            "name": faker.word(), "business_type": faker.word(),
            "description": faker.text(),
        }

    def test_list_of_businesses(self) -> None:
        """Tests if view gives all businesses."""
        response = self.client.get(
            path=reverse("api:businesses-list-create"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_create_business_no_auth(self) -> None:
        """Tests view for creation Business.

        Checks if view does not allow user to create business without
        authentication
        """
        response = self.client.post(
            path=reverse("api:businesses-list-create"),
            data=self.valid_create_data,
        )

        self.assertEqual(response.status_code, 401)

    def test_create_business_invalid_owner(self) -> None:
        """Tests view for creation Business.

        Tests if view does not allow to create business with
        user who does not belong to Owner group
        """
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            path=reverse("api:businesses-list-create"),
            data=self.invalid_create_data,
        )

        self.client.force_authenticate(user=None)

        self.assertEqual(response.status_code, 403)

    def test_create_business_valid_owner(self) -> None:
        """Checks business creation with authenticated user and valid data."""
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            path=reverse("api:businesses-list-create"),
            data=self.valid_create_data,
        )

        self.client.force_authenticate(user=None)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["owner"], self.owner.get_full_name())
