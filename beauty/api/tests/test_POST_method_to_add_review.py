"""This module is for testing the POST method that is used to create
new reviews. It tests ReviewAddView and ReviewAddSerializer.

Tests:
    *   Test that unauthorized user won't be able to access API
    *   Test that an authorized user can create a Review
    *   Test that serializer doesn't allow rating < 0
    *   Test that serializer doesn't allow rating > 5
    *   Test that serializer doesn't allow text_body to be empty
    *   Test that serializer doesn't allow text_body length > 500
    *   Test that users won't be able to review themselves

Todo:
    *   Migrate to the new URLs once they are available

"""

from django.test import TestCase
from rest_framework.test import APIClient
from api.models import CustomUser
from api.serializers.serializers_review import ReviewAddSerializer
from api.views import ReviewAddView


class TestReviewAddView(TestCase):
    """This class represents a Test case and has all the tests"""

    def setUp(self) -> None:
        """This method is called before running the tests to populate
        database with needed info
        """
        self.reviewer = {
                    "id": 1,
                    "email": "reviewer@djangotests.ua",
                    "first_name": "Рев'ювер",
                    "patronymic": "Рев'юверович",
                    "last_name": "Рев'юверенко",
                    "phone_number": "+380960000001",
                    "bio": "Пише відгуки про їжу.",
                    "rating": -2,
                    "is_active": True,
        }
        self.responder = {
                    "id": 2,
                    "email": "responder@djangotests.ua",
                    "first_name": "Майстер",
                    "patronymic": "Майстрович",
                    "last_name": "Майстренко",
                    "phone_number": "+380960000002",
                    "bio": "Зробить дві процедури за 50 гривень.",
                    "rating": 4,
                    "is_active": True,
        }

        self.user = CustomUser.objects.create(**self.reviewer)
        self.user.save()
        CustomUser.objects.create(**self.responder).save()

        self.serializer = ReviewAddSerializer
        self.view = ReviewAddView
        self.client = APIClient()
        return super().setUp()

    def test_POST_method_create_review_not_logged_user(self):
        """Only a logged user can create a review"""
        response = self.client.post(
            path='http://127.0.0.1:8000/api/v1/user/1/reviews/add/',
            data={'text_body': 'I am not a logged User', 'rating': 3}
        )
        self.assertEqual(response.status_code, 401)

    def test_POST_method_create_review_logged_user(self):
        """A logged user should be able to create a review"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            path='http://127.0.0.1:8000/api/v1/user/2/reviews/add/',
            data={'text_body': 'I am logged user', 'rating': 2}
        )
        self.assertEqual(response.status_code, 201)

    def test_POST_method_create_review_wrong_rating_min(self):
        """Rating should not be less than 0"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            path='http://127.0.0.1:8000/api/v1/user/2/reviews/add/',
            data={'text_body': 'I am logged user', 'rating': -1}
        )
        self.assertEqual(response.status_code, 400)

    def test_POST_method_create_review_wrong_rating_max(self):
        """Rating should not be more than 5"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            path='http://127.0.0.1:8000/api/v1/user/2/reviews/add/',
            data={'text_body': 'I am logged user', 'rating': 6}
        )
        self.assertEqual(response.status_code, 400)

    def test_POST_method_create_review_wrong_text_empty(self):
        """Text of the review should not be empty"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            path='http://127.0.0.1:8000/api/v1/user/2/reviews/add/',
            data={'text_body': '', 'rating': 2}
        )
        self.assertEqual(response.status_code, 400)

    def test_POST_method_create_review_wrong_text_max(self):
        """Text of the review should not exceed 500 characters"""
        self.client.force_authenticate(user=self.user)
        text = '&' * 501
        response = self.client.post(
            path='http://127.0.0.1:8000/api/v1/user/2/reviews/add/',
            data={'text_body': text, 'rating': 2}
        )
        self.assertEqual(response.status_code, 400)

    def test_POST_method_create_review_cant_review_yourself(self):
        """Users should not be able to review themselves"""
        self.client.force_authenticate(user=self.user)
        text = '&' * 501
        response = self.client.post(
            path='http://127.0.0.1:8000/api/v1/user/1/reviews/add/',
            data={'text_body': text, 'rating': 2}
        )
        self.assertEqual(response.status_code, 400)
