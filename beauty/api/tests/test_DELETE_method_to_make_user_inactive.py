"""This module is for testing DELETE method that is used to inactivate Users.

It tests perform_destroy method of CustomUserDetailRUDView.

Tests:
    *   Test that user can inactivate account
    *   Test that user can't inactivate other user's accounts
    *   Test that unauthorized users can't inactivate other user's accounts
    *   Test that can't make himself inactive if he is already deactivated

"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.models import CustomUser
from .factories import CustomUserFactory


class TestDeleteUser(TestCase):
    """This class represents a Test case for the making User inactive.

    All the neaded information is submited in the setUp method.
    """

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.user1 = CustomUserFactory.create(is_active=True)
        self.user2 = CustomUserFactory.create(is_active=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_delete_user(self):
        """User can make himself inactive."""
        response = self.client.delete(
            path=reverse("api:user-detail", kwargs={"pk": self.user1.id}),
            data={},
        )
        self.assertEquals(
            [response.status_code, CustomUser.objects.get(pk=1).is_active],
            [200, False],
        )

    def test_delete_user_wronguser(self):
        """User can't make other users inactive."""
        response = self.client.delete(
            path=reverse("api:user-detail", kwargs={"pk": self.user2.id}),
            data={},
        )
        self.assertEquals(
            [response.status_code, CustomUser.objects.get(pk=2).is_active],
            [403, True],
        )

    def test_delete_user_unauthorized(self):
        """Unauthorized person can't make other users inactive."""
        self.client.force_authenticate(user=None)
        response = self.client.delete(
            path=reverse("api:user-detail", kwargs={"pk": self.user1.id}),
            data={},
        )
        self.assertEquals(
            [response.status_code, CustomUser.objects.get(pk=1).is_active],
            [401, True],
        )

    def test_delete_user_already_inactive(self):
        """User can't make himself inactive if he is already deactivated."""
        self.user1.is_active = False
        self.user1.save()
        response = self.client.delete(
            path=reverse("api:user-detail", kwargs={"pk": self.user1.id}),
            data={},
        )
        self.assertEquals(
            [response.status_code, CustomUser.objects.get(pk=1).is_active],
            [400, False],
        )
