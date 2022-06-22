"""This module is for testing DELETE method that is used to inactivate Business."""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.models import Position
from .factories import (BusinessFactory, CustomUserFactory, GroupFactory, PositionFactory)
from api.serializers.position_serializer import PositionSerializer
from api.views_api import RemoveSpecialistFromPosition


class TestDeleteBusiness(TestCase):
    """This class represents a Test case for the making Business inactive.

    All the needed information is submitted in the setUp method.
    """

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.groups = GroupFactory.groups_for_test()
        self.specialist1 = CustomUserFactory(first_name="UserSpecialist1")
        self.specialist2 = CustomUserFactory(first_name="UserSpecialist2")
        self.specialist3 = CustomUserFactory(first_name="UserSpecialist3")
        self.specialist4 = CustomUserFactory(first_name="UserSpecialist4")
        self.user = CustomUserFactory.create()
        self.groups.specialist.user_set.add(self.specialist1)
        self.groups.specialist.user_set.add(self.specialist2)
        self.groups.specialist.user_set.add(self.specialist3)
        self.groups.specialist.user_set.add(self.specialist4)

        self.serializer = PositionSerializer
        self.queryset = Position.objects.all()
        self.view = RemoveSpecialistFromPosition.as_view()

        self.owner = CustomUserFactory(first_name="OwnerUser")
        self.groups.owner.user_set.add(self.owner)

        self.business = BusinessFactory(name="Business", owner=self.owner, is_active=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

        self.position1 = PositionFactory.create(business=self.business,
                                                specialist=[self.specialist1])
        self.position2 = PositionFactory.create(business=self.business,
                                                specialist=[self.specialist2])
        self.position3 = PositionFactory.create(business=self.business,
                                                specialist=[self.specialist3])
        self.position4 = PositionFactory.create(business=self.business,
                                                specialist=[self.specialist4])

    def test_delete_specialist_from_position_correct(self):
        """Business owner can remove specialist from position."""
        response = self.client.delete(
            path=reverse(
                viewname="api:position-delete-specialist",
                kwargs={"pk": self.position1.id, "specialist_id": self.specialist1.id},
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_specialist_from_position_by_other_user(self):
        """Other user can not remove specialist from position."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            path=reverse(
                viewname="api:position-delete-specialist",
                kwargs={"pk": self.position2.id, "specialist_id": self.specialist2.id},
            ),
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_specialist_from_position_unauthorized(self):
        """Unauthorized person can't remove specialist from position."""
        self.client.force_authenticate(user=None)
        response = self.client.delete(
            path=reverse(
                viewname="api:position-delete-specialist",
                kwargs={"pk": self.position3.id, "specialist_id": self.specialist3.id},
            ),
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_specialist_from_position_that_is_already_removed(self):
        """Owner can't remove specialist from position if it is already removed."""
        response1 = self.client.delete(
            path=reverse(
                viewname="api:position-delete-specialist",
                kwargs={"pk": self.position4.id, "specialist_id": self.specialist4.id},
            ),
        )

        response2 = self.client.delete(
            path=reverse(
                viewname="api:position-delete-specialist",
                kwargs={"pk": self.position4.id, "specialist_id": self.specialist4.id},
            ),
        )

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 400)
