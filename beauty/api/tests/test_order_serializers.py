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

Todo:
    *   Migrate to the new URLs once they are available

"""

import pytz
from django.test import TestCase
from rest_framework.exceptions import ErrorDetail

from api.serializers.order_serializers import OrderSerializer
from .factories import *

CET = pytz.timezone("Europe/Kiev")


class TestOrderSerializer(TestCase):

    def setUp(self):
        self.Serializer = OrderSerializer

        self.groups = GroupFactory.groups_for_test()
        self.specialist = CustomUserFactory(first_name="UserSpecialist")
        self.customer = CustomUserFactory(first_name="UserCustomer")
        self.position = PositionFactory(name="Position_1")
        self.service = ServiceFactory(name="Service_1", position=self.position)

        self.groups.specialist.user_set.add(self.specialist)
        self.groups.customer.user_set.add(self.customer)
        self.position.specialist.add(self.specialist)

    def test_valid_serializer(self):
        valid_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                      'specialist': self.specialist.id,
                      'service': self.service.id}

        ecxpect_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                        'specialist': self.specialist,
                        'service': self.service}

        serializer = self.Serializer(data=valid_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data, ecxpect_data)
        self.assertEqual(serializer.errors, {})
        order = serializer.save(customer=self.customer)
        self.assertEqual(order.status, 0)
        self.assertEqual(order.customer, self.customer)

    def test_invalid_serializer(self):
        invalid_data = {'start_time': timezone.datetime(2022, 5, 30, 9, 40, 16, tzinfo=CET),
                        'specialist': self.specialist.id}

        serializer = self.Serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.data, invalid_data)
        self.assertEqual(serializer.errors, {
            'service': [ErrorDetail(string='This field is required.', code='required')]})

# def test_invalid_datatype(self):
#     serializer = self.Serializer(data=[{'char': 'abc'}])
#     assert not serializer.is_valid()
#     assert serializer.validated_data == {}
#     assert serializer.data == {}
#     assert serializer.errors == {'non_field_errors': ['Invalid data. Expected a dictionary, but got list.']}
#
# def test_partial_validation(self):
#     serializer = self.Serializer(data={'char': 'abc'}, partial=True)
#     assert serializer.is_valid()
#     assert serializer.validated_data == {'char': 'abc'}
#     assert serializer.errors == {}
#
# def test_empty_serializer(self):
#     serializer = self.Serializer()
#     assert serializer.data == {'char': '', 'integer': None}
#
# def test_missing_attribute_during_serialization(self):
#     class MissingAttributes:
#         pass
#     instance = MissingAttributes()
#     serializer = self.Serializer(instance)
#     with pytest.raises(AttributeError):
#         serializer.data
#
# def test_data_access_before_save_raises_error(self):
#     def create(validated_data):
#         return validated_data
#     serializer = self.Serializer(data={'char': 'abc', 'integer': 123})
#     serializer.create = create
#     assert serializer.is_valid()
#     assert serializer.data == {'char': 'abc', 'integer': 123}
#     with pytest.raises(AssertionError):
#         serializer.save()
#
# def test_validate_none_data(self):
#     data = None
#     serializer = self.Serializer(data=data)
#     assert not serializer.is_valid()
#     assert serializer.errors == {'non_field_errors': ['No data provided']}
#
# def test_serialize_chainmap(self):
#     data = ChainMap({'char': 'abc'}, {'integer': 123})
#     serializer = self.Serializer(data=data)
#     assert serializer.is_valid()
#     assert serializer.validated_data == {'char': 'abc', 'integer': 123}
#     assert serializer.errors == {}
#
# def test_serialize_custom_mapping(self):
#     class SinglePurposeMapping(Mapping):
#         def __getitem__(self, key):
#             return 'abc' if key == 'char' else 123
#
#         def __iter__(self):
#             yield 'char'
#             yield 'integer'
#
#         def __len__(self):
#             return 2
#
#     serializer = self.Serializer(data=SinglePurposeMapping())
#     assert serializer.is_valid()
#     assert serializer.validated_data == {'char': 'abc', 'integer': 123}
#     assert serializer.errors == {}
#
# def test_custom_to_internal_value(self):
#     """
#     to_internal_value() is expected to return a dict, but subclasses may
#     return application specific type.
#     """
#     class Point:
#         def __init__(self, srid, x, y):
#             self.srid = srid
#             self.coords = (x, y)
#
#     # Declares a serializer that converts data into an object
#     class NestedPointSerializer(serializers.Serializer):
#         longitude = serializers.FloatField(source='x')
#         latitude = serializers.FloatField(source='y')
#
#         def to_internal_value(self, data):
#             kwargs = super().to_internal_value(data)
#             return Point(srid=4326, **kwargs)
#
#     serializer = NestedPointSerializer(data={'longitude': 6.958307, 'latitude': 50.941357})
#     assert serializer.is_valid()
#     assert isinstance(serializer.validated_data, Point)
#     assert serializer.validated_data.srid == 4326
#     assert serializer.validated_data.coords[0] == 6.958307
#     assert serializer.validated_data.coords[1] == 50.941357
#     assert serializer.errors == {}
#
# def test_iterable_validators(self):
#     """
#     Ensure `validators` parameter is compatible with reasonable iterables.
#     """
#     data = {'char': 'abc', 'integer': 123}
#
#     for validators in ([], (), set()):
#         class ExampleSerializer(serializers.Serializer):
#             char = serializers.CharField(validators=validators)
#             integer = serializers.IntegerField()
#
#         serializer = ExampleSerializer(data=data)
#         assert serializer.is_valid()
#         assert serializer.validated_data == data
#         assert serializer.errors == {}
#
#     def raise_exception(value):
#         raise exceptions.ValidationError('Raised error')
#
#     for validators in ([raise_exception], (raise_exception,), {raise_exception}):
#         class ExampleSerializer(serializers.Serializer):
#             char = serializers.CharField(validators=validators)
#             integer = serializers.IntegerField()
#
#         serializer = ExampleSerializer(data=data)
#         assert not serializer.is_valid()
#         assert serializer.data == data
#         assert serializer.validated_data == {}
#         assert serializer.errors == {'char': [
#             exceptions.ErrorDetail(string='Raised error', code='invalid')
#         ]}
#
# @pytest.mark.skipif(
#     sys.version_info < (3, 7),
#     reason="subscriptable classes requires Python 3.7 or higher",
# )
# def test_serializer_is_subscriptable(self):
#     assert serializers.Serializer is serializers.Serializer["foo"]
#


# class TestReviewAddView(TestCase):
#     """This class represents a Test case and has all the tests."""
#
#     def setUp(self) -> None:
#         """This method adds needed info for tests."""
#         self.reviewer = {
#                     "id": 1,
#                     "email": "reviewer@djangotests.ua",
#                     "first_name": "Reviewer",
#                     "patronymic": "Reviewer",
#                     "last_name": "Reviewer",
#                     "phone_number": "+380960000001",
#                     "bio": "Works for food",
#                     "rating": -2,
#                     "is_active": True,
#         }
#         self.responder = {
#                     "id": 2,
#                     "email": "responder@djangotests.ua",
#                     "first_name": "Responder",
#                     "patronymic": "Responder",
#                     "last_name": "Responder",
#                     "phone_number": "+380960000002",
#                     "bio": "Just a happy guy",
#                     "rating": 4,
#                     "is_active": True,
#         }
#
#         self.user = CustomUser.objects.create(**self.reviewer)
#         self.user.save()
#         CustomUser.objects.create(**self.responder).save()
#
#         self.serializer = ReviewAddSerializer
#         self.view = ReviewAddView
#         self.client = APIClient()
#         self.client.force_authenticate(user=self.user)
#
#     def test_POST_method_create_review_not_logged_user(self):
#         """Only a logged user can create a review."""
#         self.client.force_authenticate(user=None)
#         response = self.client.post(
#             path=reverse("api:review-add", kwargs={"user":2}),
#             data={"text_body": "I am not a logged User", "rating": 3}
#         )
#         self.assertEqual(response.status_code, 401)
#
#     def test_POST_method_create_review_logged_user(self):
#         """A logged user should be able to create a review"""
#         response = self.client.post(
#             path=reverse("api:review-add", kwargs={"user":2}),
#             data={"text_body": "I am logged user", "rating": 2}
#         )
#         self.assertEqual(response.status_code, 201)
#
#     def test_POST_method_create_review_wrong_rating_min(self):
#         """Rating should not be less than 0."""
#         response = self.client.post(
#             path=reverse("api:review-add", kwargs={"user":2}),
#             data={"text_body": "I am logged user", "rating": -1}
#         )
#         self.assertEqual(response.status_code, 400)
#
#     def test_POST_method_create_review_wrong_rating_max(self):
#         """Rating should not be more than 5."""
#         response = self.client.post(
#             path=reverse("api:review-add", kwargs={"user":2}),
#             data={"text_body": "I am logged user", "rating": 6}
#         )
#         self.assertEqual(response.status_code, 400)
#
#     def test_POST_method_create_review_wrong_text_empty(self):
#         """Text of the review should not be empty."""
#         response = self.client.post(
#             path=reverse("api:review-add", kwargs={"user":2}),
#             data={"text_body": "", "rating": 2}
#         )
#         self.assertEqual(response.status_code, 400)
#
#     def test_POST_method_create_review_wrong_text_max(self):
#         """Text of the review should not exceed 500 characters."""
#         text = "&" * 501
#         response = self.client.post(
#             path=reverse("api:review-add", kwargs={"user":2}),
#             data={"text_body": text, "rating": 2}
#         )
#         self.assertEqual(response.status_code, 400)
#
#     def test_POST_method_create_review_cant_review_yourself(self):
#         """Users should not be able to review themselves."""
#         response = self.client.post(
#             path=reverse("api:review-add", kwargs={"user":1}),
#             data={"text_body": "I am the best!", "rating": 2}
#         )
#         self.assertEqual(response.status_code, 400)
