"""This module is for testing PositionRetrieveUpdateDestroyView.

Tests for PositionListCreateView:
- SetUp method adds needed data for tests;
- Get 1 selected position by id;
- Put into valid id;
- Customer must be authenticated and be owner of position;
- End time euqal to start time;
- Invalid start and end time;
- Owner is allowed to put empty data;
- Delete by selected id;
- Delete by id, which doesn't exist;
"""

import json
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.models import Position
from api.views import PositionRetrieveUpdateDestroyView
from api.serializers.position_serializer import PositionSerializer
from .factories import (BusinessFactory,
                        CustomUserFactory,
                        GroupFactory,
                        PositionFactory)


class TestPositionRetrieveUpdateDestroyView(TestCase):
    """TestCase to test PositionRetrieveUpdateDestroyView."""

    def setUp(self):
        """Create business and 2 specialists."""
        self.groups = GroupFactory.groups_for_test()
        self.specialist1 = CustomUserFactory(first_name="UserSpecialist")
        self.specialist2 = CustomUserFactory(first_name="UserSpecialist2")
        self.groups.specialist.user_set.add(self.specialist1)
        self.groups.specialist.user_set.add(self.specialist2)

        self.serializer = PositionSerializer
        self.queryset = Position.objects.all()
        self.view = PositionRetrieveUpdateDestroyView.as_view()

        self.owner = CustomUserFactory(first_name="OwnerUser")
        self.groups.owner.user_set.add(self.owner)

        self.business = BusinessFactory.create(name="Hope", owner=self.owner)
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

        self.position = PositionFactory.create(name="Wyh",
                                               business=self.business,
                                               specialist=[self.specialist1],
                                               start_time="9:00:00",
                                               end_time="10:00:00",
                                               )
        self.url = "api:position-detail-list"
        self.pk = self.position.id

    def test_position_get_by_id(self):
        """Get 1 created position."""
        response = self.client.generic(
            method="GET",
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_position_get_by_id_invalid(self):
        """Get 1 created position."""
        response = self.client.generic(
            method="GET",
            path=reverse(
                self.url,
                kwargs={"pk": self.pk + 1},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_position_put_valid(self):
        """POST requests to ListCreateAPIView with valid data should create a new object."""
        response = self.client.patch(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps({"name": "Angle"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_position_put_without_authentication(self):
        """POST requests to ListCreateAPIView with no authenticate shouldn't create a new object."""
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps({"name": "Angle"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_position_put_end_time(self):
        """POST requests to ListCreateAPIView with invalid time shouldn't create a new object."""
        response = self.client.patch(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps({"end_time": "8:00:00"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_position_put_invalid_time(self):
        """POST requests to ListCreateAPIView with invalid time shouldn't create a new object."""
        response = self.client.patch(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps({
                "end_time": "8:00:00",
                "start_time": "9:00:00",
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_position_put_empty_data(self):
        """POST requests to ListCreateAPIView with empty data shouldn't create a new object."""
        response = self.client.patch(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_position_delete_by_id(self):
        """Get 1 created position."""
        response = self.client.generic(
            method="DELETE",
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
        )
        self.assertEqual(response.status_code, 204)

    def test_position_delete_by_id_invalid(self):
        """Get 1 created position."""
        response = self.client.generic(
            method="DELETE",
            path=reverse(
                self.url,
                kwargs={"pk": self.pk + 1},
            ),
        )
        self.assertEqual(response.status_code, 404)
