"""The module includes tests for CustomUser serializers.

Tests for CustomUser serializers:
- This method adds needed info for tests;
- Check serializer with valid data;
- Check serializer with invalid data;
- Check serializer with invalid data type;
- Check serializer without data;
- Check serializer with data equal None;
- Check Custom User Serializer with users' queryset data when a specialist is logged;
- Check Custom User Serializer with users' queryset data when a customer is logged;
- Check Custom User Serializer with users' queryset data when a user is not logged;
- Check serializer with customer instance data;
- Check serializer with specialist instance data;
- Deserializing a data and updating a user data with password data;
- Deserializing a data and updating a user data without password data;
- To_internal_value() is expected to return a str, but return int.

Passwords validation tests:
- This method adds needed info for tests;
- Checking valid data;
- Checking invalid data;
- Checking when password or password confirmation is null.
"""

from django.contrib.auth.hashers import (check_password, make_password)
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse

from api.models import CustomUser
from api.serializers.customuser_serializers import (CustomUserSerializer,
                                                    PasswordsValidation, CustomUserDetailSerializer)
from rest_framework.test import (APIRequestFactory, APIClient)
from rest_framework.serializers import ValidationError
from api.tests.factories import (CustomUserFactory, GroupFactory, OrderFactory)


class CustomUserSerializerTestCase(TestCase):
    """Tests for CustomUser serializers."""

    valid_data = {"email": "m6@com.ua",
                  "first_name": "Specialist_6",
                  "phone_number": "+380967470016",
                  "password": "0967478911m",
                  "confirm_password": "0967478911m",
                  "groups": ["Specialist"]}

    ecxpect_data = {"email": "m6@com.ua",
                    "first_name": "Specialist_6",
                    "phone_number": "+380967470016",
                    "password": "0967478911m",
                    "confirm_password": "0967478911m",
                    "groups": [4]}

    def setUp(self):
        """This method adds needed info for tests."""
        self.Serializer = CustomUserSerializer
        self.Detail_serializer = CustomUserDetailSerializer

        self.specialist = CustomUserFactory(first_name="User_1", email="user_1@com.ua",
                                            phone_number="+380960000001")
        self.customer = CustomUserFactory(first_name="User_2", email="user_2@com.ua",
                                          phone_number="+380960000002")
        self.specialist2 = CustomUserFactory(first_name="User_3", email="user_3@com.ua",
                                             phone_number="+380960000003")
        self.customer_order = OrderFactory(customer=self.customer, specialist=self.specialist)
        self.specialist_order = OrderFactory(customer=self.specialist, specialist=self.specialist2)

        self.groups = GroupFactory.groups_for_test()
        self.groups.specialist.user_set.add(self.specialist)
        self.groups.customer.user_set.add(self.customer)

        self.factory = APIRequestFactory()
        self.request = self.factory.get("/")

        self.client = APIClient()


    def test_valid_serializer(self):
        """Check serializer with valid data."""
        serializer = self.Serializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data, self.ecxpect_data)
        self.assertEqual(serializer.errors, {})

        user = serializer.save()
        self.assertEqual(user.email, self.ecxpect_data["email"])
        self.assertEqual(user.first_name, self.ecxpect_data["first_name"])
        self.assertEqual(user.phone_number, self.ecxpect_data["phone_number"])
        self.assertTrue(check_password(self.ecxpect_data["password"], user.password))
        with self.assertRaises(AttributeError) as ex:
            user.confirm_password
        self.assertEqual(
            "'CustomUser' object has no attribute 'confirm_password'",
            str(ex.exception),
        )

    def test_invalid_serializer(self):
        """Check serializer with invalid data."""
        invalid_data = self.valid_data.copy()
        invalid_data["phone_number"] = "invalid_phone_number"

        serializer = self.Serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.data, invalid_data)
        self.assertEqual(serializer.errors, {
            "phone_number": [ErrorDetail(string="The phone number entered is not valid.",
                                         code="invalid_phone_number")]})

    def test_invalid_datatype(self):
        """Check serializer with invalid data type."""
        invalid_data = [self.valid_data]

        serializer = self.Serializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {})
        self.assertEqual(serializer.data, {})
        self.assertEqual(serializer.errors, {"non_field_errors": [ErrorDetail(
            string="Invalid data. Expected a dictionary, but got list.", code="invalid")],
        })

    def test_empty_serializer(self):
        """Check serializer without data."""
        serializer = self.Serializer()
        self.assertEqual(serializer.data, {"email": "", "first_name": "", "patronymic": "",
                                           "last_name": "", "phone_number": "", "bio": "",
                                           "rating": None, "avatar": None, "is_active": False,
                                           "groups": [], "password": "", "confirm_password": ""})

    def test_validate_none_data(self):
        """Check serializer with data equal None."""
        data = None
        serializer = self.Serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {"non_field_errors": ["No data provided"]})

    def test_customuserserialize_customer_logged(self):
        """Check Custom User Serializer with users' queryset data when a customer is logged."""
        self.client.force_authenticate(user=self.customer)
        queryset = CustomUser.objects.all()
        response = self.client.get(path=reverse("api:user-list-create"))

        self.request.user = self.customer
        serializer = self.Serializer(queryset, many=True, context={"request": self.request})
        self.assertEqual(serializer.data, response.data)

    def test_customuserserialize_specialist_logged(self):
        """Check Custom User Serializer with users' queryset data when a specialist is logged."""
        self.client.force_authenticate(user=self.specialist)
        queryset = CustomUser.objects.all()
        response = self.client.get(path=reverse("api:user-list-create"))

        self.request.user = self.specialist
        serializer = self.Serializer(queryset, many=True, context={"request": self.request})
        self.assertEqual(serializer.data, response.data)

    def test_customuserserialize_user_no_logged(self):
        """Check Custom User Serializer with users' queryset data when a user is not logged."""
        self.client.force_authenticate(user=None)
        queryset = CustomUser.objects.all()
        response = self.client.get(path=reverse("api:user-list-create"))

        self.request.user = AnonymousUser()
        serializer = self.Serializer(queryset, many=True, context={"request": self.request})
        self.assertEqual(serializer.data, response.data)

    def test_serialize_customer_instance(self):
        """Check serializer with customer instance data."""
        self.client.force_authenticate(self.customer)
        response = self.client.get(path=reverse("api:user-detail", args=[self.customer.id]))

        self.request.user = self.customer
        serializer = self.Detail_serializer(self.customer, context={"request": self.request})
        self.assertEqual(serializer.data["customer_exist_orders"],
                         response.data["customer_exist_orders"])
        
        self.assertEqual(serializer.data["groups"], ["Customer"])
        with self.assertRaises(KeyError):
            serializer.data["password"]
            response.data["specialist_exist_orders"]

    def test_serialize_specialist_instance(self):
        """Check serializer with specialist instance data."""
        self.client.force_authenticate(self.specialist)
        response = self.client.get(path=reverse("api:user-detail", args=[self.specialist.id]))

        self.request.user = self.specialist
        serializer = self.Detail_serializer(self.specialist, context={"request": self.request})
        self.assertEqual(serializer.data["specialist_exist_orders"],
                         response.data["specialist_exist_orders"])
        self.assertEqual(serializer.data["customer_exist_orders"],
                         response.data["customer_exist_orders"])
        self.assertEqual(serializer.data["groups"], ["Specialist"])

    def test_deserialize_update_user_with_password(self):
        """Deserializing a data and updating a user data with password data."""
        data = {"first_name": "Customer_1_2", "email": "test@com.ua",
                "password": "0987654321s", "confirm_password": "0987654321s"}
        self.request.user = self.customer
        serializer = self.Detail_serializer(
            instance=self.customer, data=data,
            partial=True,
            context={"request": self.request},
        )
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(check_password(data["password"], make_password(data["password"])))
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.email, data["email"])

    def test_deserialize_update_user_without_password(self):
        """Deserializing a data and updating a user data without password data."""
        data = {"first_name": "Specialist_1_2", "email": "test@com.ua",
                "password": "", "confirm_password": ""}
        instance = self.customer
        serializer = self.Detail_serializer(
            instance=instance, data=data,
            partial=True,
            context={"request": self.request},
        )
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.email, data["email"])

    def test_custom_to_internal_value_for_groups(self):
        """To_internal_value() is expected to return a str, but return int."""
        serializer = self.Serializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        groups = serializer.validated_data["groups"]
        if groups:
            self.assertIsInstance(groups[0], int)
            self.assertIn(self.groups.specialist.id, groups)
        self.assertEqual(serializer.errors, {})


class PasswordsValidationTest(TestCase):
    """Passwords validation tests.

    Tests for checking password and password confirmation when user
    creating user or updating user data.
    """

    valid_data = {"password": "0967478911m", "confirm_password": "0967478911m"}
    invalid_data = {"password": "0967478911m", "confirm_password": "096747891"}
    null_data_one = {"password": "", "confirm_password": "096747891"}
    null_data_two = {"password": "0967478911m", "confirm_password": ""}

    def setUp(self):
        """This method adds needed info for tests."""
        self.validator = PasswordsValidation()

    def test_valid_data(self):
        """Checking valid data."""
        data = self.validator.validate(self.valid_data)
        self.assertEqual(data, self.valid_data)

    def test_invalid_data(self):
        """Checking invalid data."""
        with self.assertRaises(ValidationError) as ex:
            self.validator.validate(self.invalid_data)
        self.assertEqual(
            {"password": "Password confirmation does not match."},
            ex.exception.args[0],
        )

    def test_password_null(self):
        """Checking when password or password confirmation is null."""
        with self.assertRaises(ValidationError) as ex:
            self.validator.validate(self.null_data_one)
            self.validator.validate(self.null_data_two)
        self.assertEqual(
            {"confirm_password": "Didn`t enter the password confirmation."},
            ex.exception.args[0],
        )
