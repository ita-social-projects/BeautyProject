"""This module is for testing position ListCreatView.

Tests for PositionListCreateView:
- SetUp method adds needed data for tests;
- Get 1 created positions;
- Post valid position;
- Customer must be authenticated;
- Owner isn't allowed to post empty data.
"""

import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.serializers.position_serializer import PositionSerializer
from api.models import Position
from api.views_api import PositionListCreateView
from .factories import (BusinessFactory,
                        CustomUserFactory,
                        GroupFactory,
                        PositionFactory)


class TestPositionListCreateView(TestCase):
    """TestCase to test PositionListCreateView."""

    def setUp(self):
        """Create business and 2 specialists."""
        self.groups = GroupFactory.groups_for_test()
        self.specialist1 = CustomUserFactory(first_name="UserSpecialist")
        self.specialist2 = CustomUserFactory(first_name="UserSpecialist2")
        self.groups.specialist.user_set.add(self.specialist1)
        self.groups.specialist.user_set.add(self.specialist2)

        self.serializer = PositionSerializer
        self.queryset = Position.objects.all()
        self.serializer = PositionSerializer
        self.view = PositionListCreateView.as_view()

        self.owner = CustomUserFactory(first_name="OwnerUser")
        self.groups.owner.user_set.add(self.owner)

        self.business = BusinessFactory(name="Hope", owner=self.owner)
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

        self.position_testing = PositionFactory.build(
            name="Wyh",
            business=self.business,
        )
        self.valid_data = {
            "name": self.position_testing.name,
            "business": self.position_testing.business.id,
            "specialist": [self.specialist1.id],
        }
        self.valid_data.update(self.position_testing.working_time)

        self.url = reverse("api:position-list")

    def test_position_get_from_valid_business(self):
        """Get 1 created position."""
        self.position = PositionFactory.create(
            business=self.business,
            specialist=[self.specialist1],
        )
        response = self.client.generic(
            method="GET",
            path=self.url,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_position_post_list_create_view(self):
        """POST requests to ListCreateAPIView with valid data should create a new object."""
        response = self.client.generic(
            method="POST",
            path=self.url,
            data=json.dumps(self.valid_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

    def test_position_post_list_create_view_no_authenticate(self):
        """POST requests to ListCreateAPIView with no authenticate shouldn't create a new object."""
        self.client.force_authenticate(user=None)
        response = self.client.generic(
            method="POST",
            path=self.url,
            data=self.valid_data,
        )
        self.assertEqual(response.status_code, 401)

    def test_position_post_list_create_view_empty_data(self):
        """POST requests to ListCreateAPIView with empty data shouldn't create a new object."""
        response = self.client.generic(
            method="POST",
            path=self.url,
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_position_invalid_time(self) -> None:
        """Owner cannot create position if working time is invalid."""
        self.client.force_authenticate(user=self.owner)

        self.valid_data["Mon"] = ["10:00", "9:00"]
        response = self.client.post(
            path=self.url,
            data=self.valid_data,
        )

        self.assertEqual(response.status_code, 400)

    def test_create_position_missing_working_day(self) -> None:
        """Owner can not create position without any working day."""
        self.client.force_authenticate(user=self.owner)

        self.valid_data.pop("Mon")
        response = self.client.post(
            path=self.url,
            data=self.valid_data,
        )

        self.assertEqual(response.status_code, 400)

    def test_create_position_doesnt_fit_business(self) -> None:
        """Owner can not create position if it doesn't fit business working time."""
        self.client.force_authenticate(user=self.owner)

        # Business max time defined in factory is 20:59
        self.valid_data["Mon"] = [self.valid_data["Mon"][0], "21:00"]
        response = self.client.post(
            path=self.url,
            data=self.valid_data,
        )

        self.assertEqual(response.status_code, 400)
