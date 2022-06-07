"""This module is for testing GET method that is used to receive reviews.

It tests ReviewDisplayView, ReviewDisplayDetailView and ReviewDisplaySerializer.

"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from .factories import CustomUserFactory, ReviewFactory
from api.serializers.review_serializers import ReviewDisplaySerializer


class TestReviewDisplayView(TestCase):
    """This class represents a Test case and has all the tests."""

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.user = CustomUserFactory.create(is_active=True)
        self.first_responder = CustomUserFactory(first_name="UserSpecialist")
        self.second_responder = CustomUserFactory(first_name="UserSpecialist2")

        self.review = ReviewFactory.create(from_user=self.user, to_user=self.first_responder)
        self.review = ReviewFactory.create(from_user=self.user, to_user=self.first_responder)
        self.review = ReviewFactory.create(from_user=self.user, to_user=self.first_responder)
        self.review = ReviewFactory.create(from_user=self.user, to_user=self.second_responder)

        self.serializer = ReviewDisplaySerializer
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_method_to_obtain_all_reviews_of_specified_specialist(self) -> None:
        """Get all reviews of specified specialist."""
        response = self.client.generic(method="GET",
                                       path=reverse("api:review-get", kwargs={"to_user": 2}),
                                       )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_get_method_to_obtain_specified_review(self) -> None:
        """Get review by its id."""
        response = self.client.generic(method="GET",
                                       path=reverse("api:review-detail", kwargs={"pk": 2}),
                                       )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)

    def test_get_method_to_obtain_specified_review_with_wrong_pk(self) -> None:
        """Review with such id must exist in the database."""
        response = self.client.generic(method="GET",
                                       path=reverse("api:review-detail", kwargs={"pk": 5}),
                                       )
        self.assertEqual(response.status_code, 404)
