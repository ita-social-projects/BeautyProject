"""This module is for testing POST method that is used to create new reviews.

It tests ReviewAddView and ReviewAddSerializer.

Tests:
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
from .factories import CustomUserFactory, ReviewFactory
from api.serializers.review_serializers import ReviewAddSerializer
from api.views_api import ReviewAddView


class TestReviewAddView(TestCase):
    """This class represents a Test case and has all the tests."""

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.user = CustomUserFactory.create(is_active=True)
        self.responder = CustomUserFactory.create(is_active=True)

        self.serializer = ReviewAddSerializer
        self.view = ReviewAddView
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_method_create_review_not_logged_user(self):
        """Only a logged user can create a review."""
        self.client.force_authenticate(user=None)
        review = ReviewFactory()
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.responder.id}),
            data={"text_body": review.text_body, "rating": review.rating},
        )
        self.assertEqual(response.status_code, 401)

    def test_post_method_create_review_logged_user(self):
        """A logged user should be able to create a review."""
        review = ReviewFactory()
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.responder.id}),
            data={"text_body": review.text_body, "rating": review.rating},
        )
        self.assertEqual(response.status_code, 201)

    def test_post_method_create_review_wrong_rating_min(self):
        """Rating should not be less than 0."""
        review = ReviewFactory(rating=-5)
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.responder.id}),
            data={"text_body": review.text_body, "rating": review.rating},
        )
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_review_wrong_rating_max(self):
        """Rating should not be more than 5."""
        review = ReviewFactory(rating=6)
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.responder.id}),
            data={"text_body": review.text_body, "rating": review.rating},
        )
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_review_wrong_text_empty(self):
        """Text of the review should not be empty."""
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.responder.id}),
            data={"text_body": "", "rating": 2},
        )
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_review_wrong_text_max(self):
        """Text of the review should not exceed 500 characters."""
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.responder.id}),
            data={"text_body": ("&" * 501), "rating": 2},
        )
        self.assertEqual(response.status_code, 400)

    def test_post_method_create_review_cant_review_yourself(self):
        """Users should not be able to review themselves."""
        response = self.client.post(
            path=reverse("api:review-add", kwargs={"user": self.user.id}),
            data={"text_body": "I am the best!", "rating": 2},
        )
        self.assertEqual(response.status_code, 400)
