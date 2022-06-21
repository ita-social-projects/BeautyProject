"""This module is for testing GET method that is used to receive reviews.

It tests ReviewDisplayView, ReviewDisplayDetailView and ReviewDisplaySerializer.

"""
import json

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from .factories import CustomUserFactory, ReviewFactory
from api.serializers.review_serializers import ReviewDisplaySerializer


class TestReviewDisplayView(TestCase):
    """This class represents a Test case and has all the tests."""

    def setUp(self) -> None:
        """This method adds needed info for tests."""
        self.user = CustomUserFactory.create()
        self.first_responder = CustomUserFactory(first_name="UserSpecialist")
        self.second_responder = CustomUserFactory(first_name="UserSpecialist2")

        self.review = ReviewFactory.create(
            from_user=self.user, to_user=self.first_responder,
        )
        ReviewFactory.create(from_user=self.user, to_user=self.first_responder)
        ReviewFactory.create(from_user=self.user, to_user=self.first_responder)

        self.review_inaccessible = ReviewFactory.create(
            from_user=self.first_responder, to_user=self.second_responder,
        )

        self.serializer = ReviewDisplaySerializer
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_method_to_obtain_all_reviews_of_specified_specialist(self) -> None:
        """Get all reviews of specified specialist."""
        response = self.client.generic(method="GET",
                                       path=reverse(
                                           "api:review-get",
                                           kwargs={"to_user": self.first_responder.id},
                                       ),
                                       )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_get_method_to_obtain_all_reviews_of_specified_specialist_invalid(self) -> None:
        """Get all reviews of specified specialist."""
        response = self.client.generic(method="GET",
                                       path=reverse(
                                           "api:review-get",
                                           kwargs={"to_user": 9999},
                                       ),
                                       )
        self.assertEqual(response.status_code, 404)

    def test_get_method_to_obtain_specified_review(self) -> None:
        """Get review by its id."""
        response = self.client.generic(
            method="GET",
            path=reverse("api:review-detail",
                         kwargs={"pk": self.review.id},
                         ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)

    def test_put_method_to_update_specified_review(self) -> None:
        """Get review by its id."""
        response = self.client.put(
            path=reverse("api:review-detail",
                         kwargs={"pk": self.review.id},
                         ),
            data=json.dumps({"text_body": "Hello there",
                             "id": self.review.id,
                             "rating": self.review.rating,
                             "date_of_publication": str(self.review.date_of_publication),
                             "to_user": self.review.to_user.id,
                             "from_user": self.review.from_user.id,
                             }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)

    def test_put_method_to_update_specified_review_invalid(self) -> None:
        """Get review by its id."""
        response = self.client.put(
            path=reverse("api:review-detail",
                         kwargs={"pk": self.review_inaccessible.id},
                         ),
            data=json.dumps({"text_body": "Hello there"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_patch_method_to_update_specified_review(self) -> None:
        """Get review by its id."""
        response = self.client.patch(
            path=reverse("api:review-detail",
                         kwargs={"pk": self.review.id},
                         ),
            data=json.dumps({"text_body": "Hello there"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)

    def test_patch_method_to_update_specified_review_invalid(self) -> None:
        """Get review by its id."""
        response = self.client.patch(
            path=reverse("api:review-detail",
                         kwargs={"pk": self.review_inaccessible.id},
                         ),
            data=json.dumps({"text_body": "Hello there"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_method_to_delete_specified_review(self) -> None:
        """Get review by its id."""
        response = self.client.delete(
            path=reverse("api:review-detail",
                         kwargs={"pk": self.review.id},
                         ),
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_method_to_delete_specified_review_invalid(self) -> None:
        """Get review by its id."""
        response = self.client.delete(
            path=reverse("api:review-detail",
                         kwargs={"pk": self.review_inaccessible.id},
                         ),
        )

        self.assertEqual(response.status_code, 403)

    def test_get_method_to_obtain_specified_review_with_wrong_pk(self) -> None:
        """Review with such id must exist in the database."""
        response = self.client.generic(method="GET",
                                       path=reverse("api:review-detail", kwargs={"pk": 5}),
                                       )
        self.assertEqual(response.status_code, 404)
