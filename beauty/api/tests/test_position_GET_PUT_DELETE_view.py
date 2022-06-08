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
from api.views_api import PositionRetrieveUpdateDestroyView
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
        self.serializer = PositionSerializer
        self.view = PositionRetrieveUpdateDestroyView.as_view()

        self.owner = CustomUserFactory(first_name="OwnerUser")
        self.groups.owner.user_set.add(self.owner)

        self.business = BusinessFactory(name="Hope", owner=self.owner)
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

        self.position_testing = PositionFactory.create(
            business=self.business,
        )
        self.pk = self.position_testing.id
        self.position_testing = {
            "name": self.position_testing.name,
            "business": self.business.id,
            "specialist": [self.specialist1.id],
            "start_time": str(self.position_testing.start_time.time()),
            "end_time": str(self.position_testing.end_time.time()),
        }

        self.url = "api:position-detail-list"

    def test_position_get_by_id(self):
        """Get 1 created position."""
        response = self.client.get(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_position_get_by_id_invalid(self):
        """Try to get not created position."""
        response = self.client.get(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk + 10},
            ),
        )
        self.assertEqual(response.status_code, 404)

    def test_position_put_valid(self):
        """PUT valid data."""
        response = self.client.put(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps(self.position_testing),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_position_put_without_authentication(self):
        """Try to PUT without authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.put(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps(self.position_testing),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_position_put_end_time(self):
        """Try to PUT invalid time."""
        self.position_testing["end_time"] = self.position_testing["start_time"]
        response = self.client.put(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
            data=json.dumps(self.position_testing),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_position_put_empty_data(self):
        """Try to PUT empty data."""
        response = self.client.put(
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_position_delete_by_id(self):
        """Delete 1 created position."""
        response = self.client.generic(
            method="DELETE",
            path=reverse(
                self.url,
                kwargs={"pk": self.pk},
            ),
        )
        self.assertEqual(response.status_code, 204)

    def test_position_delete_by_id_invalid(self):
        """Try to delete not created position."""
        response = self.client.generic(
            method="DELETE",
            path=reverse(
                self.url,
                kwargs={"pk": self.pk + 1},
            ),
        )
        self.assertEqual(response.status_code, 404)
