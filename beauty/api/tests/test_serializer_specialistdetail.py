"""The module includes tests for SpecialistDetail serializers.

Tests for SpecialistDetail serializers:

- Tests if view gives info about existing specialist;
- Tests if view gives info about unexisting specialist;
- Check serializer with specialist instance data that should see all users.
"""
from django.test import TestCase
from rest_framework.reverse import reverse
from api.serializers.customuser_serializers import SpecialistDetailSerializer
from rest_framework.test import (APIRequestFactory, APIClient)
from api.tests.factories import (CustomUserFactory, GroupFactory, OrderFactory, ReviewFactory)


class SpecialistDetailSerializerTestCase(TestCase):
    """Tests for SpecialistDetail serializers."""

    def setUp(self):
        """This method adds needed info for tests."""
        self.Specialist_serializer = SpecialistDetailSerializer

        self.specialist = CustomUserFactory(first_name="User_1", email="user_1@com.ua",
                                            phone_number="+380960000001")
        self.customer = CustomUserFactory(first_name="User_2", email="user_2@com.ua",
                                          phone_number="+380960000002")
        self.specialist2 = CustomUserFactory(first_name="User_3", email="user_3@com.ua",
                                             phone_number="+380960000003")
        self.customer_order = OrderFactory(customer=self.customer, specialist=self.specialist)
        self.specialist_order = OrderFactory(customer=self.specialist, specialist=self.specialist2)
        self.review = ReviewFactory(text_body="fine", rating=4,
                                    from_user=self.customer, to_user=self.specialist)
        self.review2 = ReviewFactory(text_body="very nice", rating=5,
                                     from_user=self.specialist, to_user=self.specialist2)

        self.groups = GroupFactory.groups_for_test()
        self.groups.specialist.user_set.add(self.specialist)
        self.groups.customer.user_set.add(self.customer)

        self.factory = APIRequestFactory()
        self.request = self.factory.get("/")

        self.client = APIClient()

    def test_get_existed_specialist(self):
        """Tests if view gives info about existing specialist."""
        response = self.client.get(path=reverse("api:specialist-detail", args=[self.specialist.id]))

        self.assertEqual(response.status_code, 200)

    def test_get_unexisted_specialist(self):
        """Tests if view gives info about unexisting specialist."""
        response = self.client.get(path=reverse("api:specialist-detail", args=[self.customer.id]))

        self.assertEqual(response.status_code, 404)

    def test_serialize_specialist_instance(self):
        """Check serializer with specialist instance data that should see all users."""
        response = self.client.get(path=reverse("api:specialist-detail", args=[self.specialist.id]))

        serializer = self.Specialist_serializer(self.specialist, context={"request": self.request})

        self.assertEqual(serializer.data["specialist_reviews"], response.data["specialist_reviews"])
        self.assertEqual(serializer.data["make_order"], response.data["make_order"])
        with self.assertRaises(KeyError):
            response.data["customer_exist_orders"]
            response.data["customer_reviews"]
            response.data["specialist_exist_orders"]
