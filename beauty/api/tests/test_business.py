from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from faker import Faker

from .factories import UserFactory, BusinessFactory, PositionFactory
from beauty.utils import get_random_start_end_datetime

User = get_user_model()
faker = Faker()


class BusinessModelTest(TestCase):
    def setUp(self) -> None:
        self.owner_group = Group.objects.create(name="Owner")
        self.specialist_group = Group.objects.create(name="Specialist")

        self.owner = UserFactory.create()
        self.owner_group.user_set.add(self.owner)

        self.specialist1 = UserFactory.create()
        self.specialist2 = UserFactory.create()

        self.business = BusinessFactory.create()

        self.specialist_group.user_set.add(self.specialist1)
        self.specialist_group.user_set.add(self.specialist2)

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
        self.business1 = BusinessFactory()
        self.business2 = BusinessFactory()

        self.client_group = Group.objects.create(name="Client")
        self.owner_group = Group.objects.create(name="Owner")
        # self.specialist_group = Group.objects.create(name="Specialist")

        self.test_client = UserFactory.create()
        self.client_group.user_set.add(self.test_client)
        self.owner = UserFactory.create()
        self.owner_group.user_set.add(self.owner)
        # self.owner = UserFactory()
        # self.owner_group.user_set.add(self.owner)

    def test_list_of_businesses(self) -> None:
        response = self.client.get(
            path=reverse("api:business-list-create")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
