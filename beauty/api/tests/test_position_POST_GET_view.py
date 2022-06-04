"""This module is for testing position ListCreatView.

Tests for PositionListCreateView:
- SetUp method adds needed data for tests;
- Get 1 created positions;
- Post valid position;
- Customer must be authenticated;
- Start time must go before end time;
- Owner isn't allowed to post empty data.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.serializers.position_serializer import PositionSerializer
from api.models import Position
from api.views import PositionListCreateView
from .factories import BusinessFactory, CustomUserFactory, GroupFactory, PositionFactory


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
        self.view = PositionListCreateView.as_view()

        self.owner = CustomUserFactory(first_name="OwnerUser")
        self.groups.owner.user_set.add(self.owner)

        self.business = BusinessFactory(name="Hope", owner=self.owner)
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

        # Dict needed for successful POST method. Factory won't work
        self.position_testing = {
            "name": "Wyh",
            "business": self.business.id,
            "specialist": [self.specialist1.id, self.specialist2.id],
            "start_time": "10:51:00",
            "end_time": "13:51:00",
        }

    def test_position_get_from_valid_business(self):
        """Get 1 created position."""
        self.position = PositionFactory.create(name="Wyh",
                                               business=self.business,
                                               specialist=[self.specialist1],
                                               )
        resp = self.client.generic(method="GET",
                                   path=reverse("api:position-list"),
                                   )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_position_post_list_create_view(self):
        """POST requests to ListCreateAPIView with valid data should create a new object."""
        response = self.client.post(path=reverse("api:position-list"),
                                    data=self.position_testing,
                                    )
        self.assertEqual(response.status_code, 201)

    def test_position_post_list_create_view_no_authenticate(self):
        """POST requests to ListCreateAPIView with no authenticate shouldn't create a new object."""
        self.client.force_authenticate(user=None)
        response = self.client.post(path=reverse("api:position-list"),
                                    data=self.position_testing,
                                    )
        self.assertEqual(response.status_code, 401)

    def test_position_post_list_create_view_invalid_time(self):
        """POST requests to ListCreateAPIView with invalid time shouldn't create a new object."""
        self.position_testing["end_time"] = "9:51:00"
        response = self.client.post(path=reverse("api:position-list"),
                                    data=self.position_testing,
                                    )
        self.assertEqual(response.status_code, 400)

    def test_position_post_list_create_view_empty_data(self):
        """POST requests to ListCreateAPIView with empty data shouldn't create a new object."""
        response = self.client.post(path=reverse("api:position-list"),
                                    data={},
                                    )
        self.assertEqual(response.status_code, 400)
