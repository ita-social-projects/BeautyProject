"""This module is for testing POST method that is used to create new reviews.

It tests ReviewAddView and ReviewAddSerializer.

Tests:
    *   Test that user can't review a non specialist
    *   Test that unauthorized user won't be able to access API
    *   Test that an authorized user can create a Review
    *   Test that serializer doesn't allow rating < 0
    *   Test that serializer doesn't allow rating > 5
    *   Test that serializer doesn't allow text_body to be empty
    *   Test that serializer doesn't allow text_body length > 500
    *   Test that users won't be able to review themselves

"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.serializers.review_serializers import ReviewAddSerializer
from api.views_api import ReviewAddView
from .factories import (CustomUserFactory,
                        GroupFactory,
                        ReviewFactory)


class TestReviewAddView(TestCase):
    """This class represents a Test case and has all the tests."""

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.groups = GroupFactory.groups_for_test()
        self.reviewer = CustomUserFactory.create()
        self.reviewee = CustomUserFactory.create()
        self.nonspecialist = CustomUserFactory.create()
        self.groups.specialist.user_set.add(self.reviewee)
        self.review = ReviewFactory.build()
        self.data = {
            "text_body": self.review.text_body,
            "rating": self.review.rating,
        }

        self.serializer = ReviewAddSerializer
        self.view = ReviewAddView
        self.client = APIClient()
        self.client.force_authenticate(user=self.reviewer)

    def test_post_method_create_review_non_specialist(self):
        """A logged user can't review a nonspecialist."""
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.nonspecialist.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_review_not_logged_user(self):
        """Only a logged user can create a review."""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.reviewee.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 401)

    def test_post_method_create_review_logged_user(self):
        """A logged user should be able to create a review."""
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.reviewee.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 201)

    def test_post_method_create_review_wrong_rating_min(self):
        """Rating should not be less than 0."""
        self.data["rating"] = -5
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.reviewee.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_review_wrong_rating_max(self):
        """Rating should not be more than 5."""
        self.data["rating"] = 10
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.reviewee.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_review_wrong_text_empty(self):
        """Text of the review should not be empty."""
        self.data["text_body"] = ""
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.reviewee.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_review_wrong_text_max(self):
        """Text of the review should not exceed 500 characters."""
        self.data["text_body"] = "%" * 501
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.reviewee.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_review_cant_review_yourself(self):
        """Users should not be able to review themselves."""
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.reviewer.id}),
            data=self.data,
        )
        self.assertEqual(response.status_code, 400)
