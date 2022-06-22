"""This module is for testing views for business editing.

It tests TestAllOrOwnerBusinessesListCreateAPIView and TestOwnerBusinessDetailRUDView.

BusinessesListCreateAPIView tests:
    *   Test that Unauthenticated user can not view list of his/her all businesses.
    *   Test that Authenticated user(owner) can view list of all his/her businesses.

BusinessDetailRUDView tests:
    *   Test that Unauthenticated user can view only basic business details.
    *   Test that Someone authenticated can view only basic business details.
    *   Test that Owner of the business can access its business edit view.
    *   Test that POST method is prohibited in the edit window.
    *   Test that Owner cannot drop his/her business to another user.
    *   Test that Owner cannot change his/her business creation date/time.
    *   Test that The owner cannot use a business name that is too long.
    *   Test that The owner cannot use a business type that is too long.
    *   Test that The owner cannot use a business address that is too long.
    *   Test that The owner cannot use a business description that is too long.
    *   Test that Owner can edit changeable business info fields.

"""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from .factories import (BusinessFactory, CustomUserFactory, GroupFactory)


class BusinessesListCreateAPIView(TestCase):
    """Class for testing AllOrOwnerBusinessesListCreateAPIView."""

    def setUp(self):
        """Create all necessary data for tests."""
        self.client = APIClient()
        self.groups = GroupFactory.groups_for_test()
        self.owner = CustomUserFactory()
        self.another_user = CustomUserFactory.create()
        self.groups.owner.user_set.add(self.owner)
        self.groups.owner.user_set.add(self.another_user)
        self.business = BusinessFactory.create(owner=self.owner)

    def test_get_method_for_specific_owner_businesses_view_by_unauthenticated_user(self):
        """Unauthenticated user can not view list of his/her all businesses."""
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse(
            viewname="api:businesses-list-create",
            kwargs={}),
        )
        self.assertEqual(response.status_code, 401)

    def test_get_method_for_specific_owner_businesses_view_by_real_owner_of_business(self):
        """Authenticated user(owner) can view list of all his/her businesses."""
        self.client.force_authenticate(user=self.business.owner)
        response = self.client.get(reverse(
            viewname="api:businesses-list-create",
            kwargs={}),
        )
        self.assertEqual(response.status_code, 200)


class BusinessDetailRUDView(TestCase):
    """Class for testing view for editing business info."""

    def setUp(self):
        """Create all necessary data for tests."""
        self.client = APIClient()
        self.groups = GroupFactory.groups_for_test()
        self.owner = CustomUserFactory()
        self.another_user = CustomUserFactory.create()
        self.groups.owner.user_set.add(self.owner)
        self.groups.owner.user_set.add(self.another_user)
        self.business = BusinessFactory.create(owner=self.owner)
        self.path = reverse(
            viewname="api:business-detail",
            kwargs={
                "pk": self.business.id,
            })
        self.valid_business_info = {
            "name": "New name",
            "business_type": "New type",
            "address": "New address",
            "description": "New description",
        }
        self.full_business_info = {
            "owner": self.another_user.id,
            "name": "New name",
            "business_type": "New type",
            "address": "New address",
            "description": "New description",
        }
        self.invalid_business_owner = {
            "owner": "New owner",
        }
        self.invalid_business_create_at = {
            "created_at": "2020-01-01T13:21:24.735942Z",
        }
        self.invalid_business_name = {
            "name": "New info" * 500,
        }
        self.invalid_business_type = {
            "business_type": "New info" * 500,
        }
        self.invalid_business_address = {
            "address": "New info" * 500,
        }
        self.invalid_business_description = {
            "description": "New info" * 500,
        }

    def test_get_method_for_edit_view_by_unauthenticated_user(self):
        """Unauthenticated user can view only basic business details."""
        self.client.force_authenticate(user=None)
        response = self.client.get(
            path=reverse(
                viewname="api:business-detail",
                kwargs={
                    "pk": self.business.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 401)
        self.assertIs(response.data.get("id"), None)

    def test_get_method_for_edit_view_by_someone_else(self):
        """Someone authenticated can view only basic business details."""
        self.client.force_authenticate(user=self.another_user)
        response = self.client.get(
            path=reverse(
                viewname="api:business-detail",
                kwargs={
                    "pk": self.business.id,
                },
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIs(response.data.get("id"), None)

    def test_get_method_for_edit_view_by_real_owner_of_business(self):
        """Owner of the business can access its business edit view."""
        self.client.force_authenticate(user=self.business.owner)
        response = self.client.get(
            path=reverse(
                viewname="api:business-detail",
                kwargs={
                    "pk": self.business.id,
                }),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNot(response.data.get("created_at"), None)

    def test_post_method_for_edit_view(self):
        """POST method is prohibited in the edit window."""
        self.client.force_authenticate(user=self.business.owner)
        response = self.client.post(path=self.path, data=self.valid_business_info)
        self.assertEqual(response.status_code, 405)

    def test_patch_method_for_edit_view_with_field_business_owner(self):
        """Owner cannot drop his/her business to another user."""
        self.client.force_authenticate(user=self.business.owner)
        response = self.client.patch(path=self.path, data=self.invalid_business_owner)
        self.assertEqual(response.status_code, 400)

    def test_patch_method_for_edit_view_with_field_business_created_at(self):
        """Owner cannot change his/her business creation date/time."""
        self.client.force_authenticate(user=self.business.owner)
        save_create_at = self.business.created_at
        self.client.patch(path=self.path, data=self.invalid_business_create_at)
        self.assertEqual(save_create_at, self.business.created_at)

    def test_patch_method_for_edit_view_with_invalid_business_name(self):
        """The owner cannot use a business name that is too long."""
        self.client.force_authenticate(user=self.business.owner)
        response = self.client.patch(path=self.path, data=self.invalid_business_name)
        self.assertEqual(response.status_code, 400)

    def test_patch_method_for_edit_view_with_invalid_business_type(self):
        """The owner cannot use a business type that is too long."""
        self.client.force_authenticate(user=self.business.owner)
        response = self.client.patch(path=self.path, data=self.invalid_business_type)
        self.assertEqual(response.status_code, 400)

    def test_patch_method_for_edit_view_with_invalid_business_address(self):
        """The owner cannot use a business address that is too long."""
        self.client.force_authenticate(user=self.business.owner)
        response = self.client.patch(path=self.path, data=self.invalid_business_address)
        self.assertEqual(response.status_code, 400)

    def test_patch_method_for_edit_view_with_invalid_business_description(self):
        """The owner cannot use a business description that is too long."""
        self.client.force_authenticate(user=self.business.owner)
        response = self.client.patch(path=self.path, data=self.invalid_business_description)
        self.assertEqual(response.status_code, 400)

    def test_patch_method_for_edit_view_with_valid_business_fields(self):
        """Owner can edit changeable business info fields."""
        self.client.force_authenticate(user=self.business.owner)
        response = self.client.patch(path=self.path, data=self.valid_business_info)
        self.assertEqual(response.status_code, 200)
