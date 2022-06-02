"""The module includes tests for CustomUser serializers.

Tests for CustomUser serializers:
- This method adds needed info for tests;
- Check serializer with valid data;
- Check serializer with invalid data;
- Check serializer with invalid data type;
- Check serializer without data;
- Check serializer with data equal None;
- Serialize all users with relative hyperlinks using CustomUserSerializer;
- Serialize all users with reverse many to many retrieve using CustomUserSerializer;
- Deserializing a data and creating a new user;
- Deserializing a data and updating a user data.

Passwords validation tests:
- This method adds needed info for tests;
- Checking valid data;
- Checking invalid data;
- Checking when password or password confirmation is null.
"""

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from rest_framework.exceptions import ErrorDetail

from api.serializers.customuser_serializers import (CustomUserSerializer,
                                                    PasswordsValidation, CustomUserDetailSerializer)
from rest_framework.test import APIRequestFactory
from rest_framework.serializers import ValidationError
from api.tests.factories import CustomUserFactory, GroupFactory


factory = APIRequestFactory()
request = factory.get("/")


class CustomUserSerializerTestCase(TestCase):
    """Tests for CustomUser serializers."""

    valid_data = {"email": "m6@com.ua",
                  "first_name": "Specialist_6",
                  "phone_number": "+380967470016",
                  "password": "0967478911m",
                  "confirm_password": "0967478911m"}

    ecxpect_data = {"email": "m6@com.ua",
                    "first_name": "Specialist_6",
                    "phone_number": "+380967470016",
                    "password": "0967478911m",
                    "confirm_password": "0967478911m"}

    ecxpect_query = [{"url": "/api/v1/user/1/", "id": 1, "email": "user_1@com.ua",
                      "first_name": "User_1", "patronymic": "", "last_name": "",
                      "phone_number": "+380960000001", "bio": None, "rating": 0,
                      "avatar": "/media/default_avatar.jpeg", "is_active": False,
                      "groups": ["Specialist"], "specialist_orders": [], "customer_orders": []},
                     {"url": "/api/v1/user/2/", "id": 2, "email": "user_2@com.ua",
                      "first_name": "User_2", "patronymic": "", "last_name": "",
                      "phone_number": "+380960000002", "bio": None, "rating": 0,
                      "avatar": "/media/default_avatar.jpeg", "is_active": False,
                      "groups": ["Customer"], "specialist_orders": [], "customer_orders": []}]

    def setUp(self):
        """This method adds needed info for tests."""
        self.Serializer = CustomUserSerializer
        self.Detail_serializer = CustomUserDetailSerializer

        self.specialist = CustomUserFactory(first_name="User_1", email="user_1@com.ua",
                                            phone_number="+380960000001")
        self.customer = CustomUserFactory(first_name="User_2", email="user_2@com.ua",
                                          phone_number="+380960000002")
        self.queryset = [self.specialist, self.customer]

        self.groups = GroupFactory.groups_for_test()
        self.groups.specialist.user_set.add(self.specialist)
        self.groups.customer.user_set.add(self.customer)

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

    def test_relative_hyperlinks(self):
        """Serialize all users with relative hyperlinks using CustomUserSerializer."""
        serializer = self.Serializer(self.queryset, many=True, context={"request": None})
        self.assertEqual(serializer.data, self.ecxpect_query)

    def test_reverse_many_to_many_retrieve(self):
        """Serialize all users with reverse many to many retrieve using CustomUserSerializer."""
        for obj in self.ecxpect_query:
            obj["url"] = f"http://testserver{obj['url']}"
            obj["avatar"] = f"http://testserver{obj['avatar']}"
        serializer = self.Serializer(self.queryset, many=True, context={"request": request})
        with self.assertNumQueries(6):
            self.assertEqual(serializer.data, self.ecxpect_query)

    def test_deserialize_create_user(self):
        """Deserializing a data and creating a new user."""
        data = {"url": "http://testserver/api/v1/user/3/",
                "id": 3,
                "email": "m6@com.ua",
                "first_name": "Specialist_6",
                "patronymic": "PSpecialist_6",
                "last_name": "LSpecialist_6",
                "phone_number": "+380967470016",
                "bio": "Specialist_6",
                "rating": 0,
                "is_active": True,
                "groups": ["Specialist"],
                "specialist_orders": [],
                "customer_orders": [],
                "password": "0967478911m",
                "confirm_password": "0967478911m"}
        serializer = self.Serializer(
            data=data,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(raise_exception=True))
        obj = serializer.save()
        data.pop("confirm_password")
        data.pop("password")
        data["avatar"] = "http://testserver/media/default_avatar.jpeg"
        self.assertEqual(serializer.data, data)
        self.assertEqual(obj.email, "m6@com.ua")

    def test_deserialize_update_user(self):
        """Deserializing a data and updating a user data."""
        data = {"first_name": "Specialist_1_1", "email": "test@com.ua"}
        instance = self.queryset[0]
        serializer = self.Detail_serializer(
            instance=instance, data=data,
            partial=True,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()
        self.assertEqual(serializer.data["first_name"], data["first_name"])
        self.assertEqual(serializer.data["email"], data["email"])


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
