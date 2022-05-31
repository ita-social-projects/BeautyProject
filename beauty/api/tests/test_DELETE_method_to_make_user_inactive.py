"""This module is for testing DELETE method that is used to inactivate Users.

It perform_destroy method of CustomUserDetailRUDView.
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


class TestDeleteUser(TestCase):
    """This class represents a Test case and has all the tests."""

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.user_data_1 = {
            "id": 1,
            "email": "user1@djangotests.ua",
            "first_name": "Reviewer",
            "patronymic": "Reviewer",
            "last_name": "Reviewer",
            "phone_number": "+380960000001",
            "bio": "Works for food",
            "rating": -2,
            "is_active": True,
        }

        self.user_data_2 = {
            "id": 2,
            "email": "user2@djangotests.ua",
            "first_name": "Reviewer",
            "patronymic": "Reviewer",
            "last_name": "Reviewer",
            "phone_number": "+380960000002",
            "bio": "Works for food",
            "rating": -2,
            "is_active": True,
        }

        self.user1 = CustomUser.objects.create(**self.user_data_1)
        self.user2 = CustomUser.objects.create(**self.user_data_2)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_delete_user(self):
        """User can make himself inactive."""
        response = self.client.delete(
            path=reverse("api:user-detail", kwargs={"pk": 1}),
            data={},
        )
        self.assertEquals(
            [response.status_code, CustomUser.objects.get(pk=1).is_active],
            [200, False],
        )

    def test_delete_user_wronguser(self):
        """User can't make other users inactive."""
        response = self.client.delete(
            path=reverse("api:user-detail", kwargs={"pk": 2}),
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
            path=reverse("api:user-detail", kwargs={"pk": 1}),
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
            path=reverse("api:user-detail", kwargs={"pk": 1}),
            data={},
        )
        self.assertEquals(
            [response.status_code, CustomUser.objects.get(pk=1).is_active],
            [400, False],
        )
