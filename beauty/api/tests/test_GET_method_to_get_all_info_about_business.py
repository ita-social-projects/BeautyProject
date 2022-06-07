"""This module is for testing GET method that is used to get all info about business."""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from .factories import CustomUserFactory, BusinessFactory
from api.serializers.business_serializers import BusinessGetAllInfoSerializers


class TestBusinessDisplayView(TestCase):
    """This class represents a Test case and has all the tests."""

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.owner = CustomUserFactory(first_name="OwnerUser")

        self.business1 = BusinessFactory.create(name="Business1", owner=self.owner)
        self.business2 = BusinessFactory.create(name="Business1", owner=self.owner)

        self.serializer = BusinessGetAllInfoSerializers
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_get_method_to_obtain_all_info_about_business(self) -> None:
        """Get all info about special business."""
        response = self.client.generic(method="GET",
                                       path=reverse(
                                           "api:business-detail",
                                           kwargs={"pk": self.business1.id},
                                       ),
                                       )

        self.assertEqual(response.status_code, 200)

    def test_get_method_404_with_wrong_pk(self) -> None:
        """Business with such id is not exist in database."""
        response = self.client.generic(method="GET",
                                       path=reverse("api:business-detail", kwargs={"pk": 10101283}),
                                       )

        self.assertEqual(response.status_code, 404)

    def test_get_method_to_check_get_for_few(self) -> None:
        """Get all info about two special business."""
        response1 = self.client.generic(method="GET",
                                        path=reverse(
                                            "api:business-detail",
                                            kwargs={"pk": self.business1.id},
                                        ),
                                        )

        response2 = self.client.generic(method="GET",
                                        path=reverse(
                                            "api:business-detail",
                                            kwargs={"pk": self.business2.id},
                                        ),
                                        )

        self.assertEqual(response1.status_code, response2.status_code)
