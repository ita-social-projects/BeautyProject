from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient

from faker import Faker

from .factories import (
    OwnerFactory, ClientFactory, SpecialistFactory, BusinessFactory, 
    PositionFactory
)
from beauty.utils import get_random_start_end_datetime

User = get_user_model()
faker = Faker()


class BusinessModelTest(TestCase):
    def setUp(self) -> None:
        self.owner = OwnerFactory.create()

        self.specialist1 = SpecialistFactory.create()
        self.specialist2 = SpecialistFactory.create()

        self.business = BusinessFactory.create()

        self.position = PositionFactory.create()
        self.position.specialist.add(self.specialist2)
        self.business.position_set.add(self.position)

    def test_create_position_method(self) -> None:
        start_time, end_time = get_random_start_end_datetime()
        position = self.business.create_position(
            faker.word(), self.specialist1, start_time, end_time
        )
        all_positions = self.business.position_set.all()

        self.assertIn(position, all_positions)
        self.assertEqual(len(all_positions), 2)

    def test_get_all_specialist_method(self) -> None:
        start_time, end_time = get_random_start_end_datetime()
        self.business.create_position(
            faker.word(), self.specialist1, start_time, end_time
        )
        all_specialists = self.business.get_all_specialists()

        self.assertIn(self.specialist1, all_specialists)
        self.assertIn(self.specialist2, all_specialists)
        self.assertEqual(len(all_specialists), 2)


class BusinessListCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.business1 = BusinessFactory.create()
        self.business2 = BusinessFactory.create()

        self.test_client = ClientFactory.create()
        self.owner = OwnerFactory.create()

        self.valid_create_data = {
            "name": faker.word(), "type": faker.word(),
            "description": faker.text(), "owner": self.owner.id
        }
        self.invalid_create_data = {
            "name": faker.word(), "type": faker.word(),
            "description": faker.text(), "owner": self.test_client.id
        }

    def test_list_of_businesses(self) -> None:
        response = self.client.get(
            path=reverse("api:business-list-create")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_create_business_no_auth(self) -> None:
        response = self.client.post(
            path=reverse("api:business-list-create"),
            data=self.valid_create_data
        )

        self.assertEqual(response.status_code, 401)

    def test_create_business_invalid_owner(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_client)

        response = self.client.post(
            path=reverse("api:business-list-create"),
            data=self.invalid_create_data
        )

        self.assertEqual(response.status_code, 400)

    def test_create_business_invalid_owner(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_client)

        response = self.client.post(
            path=reverse("api:business-list-create"),
            data=self.valid_create_data
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["owner"], self.owner.get_full_name())