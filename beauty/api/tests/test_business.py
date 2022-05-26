from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from faker import Factory

from random import randint
from datetime import datetime, timedelta

from .factories import UserFactory, BusinessFactory, PositionFactory

User = get_user_model()
faker = Factory.create()


def get_random_start_end_datetime():
    start_time = datetime(
            2022, randint(1, 12), randint(1, 31), randint(0, 23)
        )
    return start_time, start_time + timedelta(hours=8)


class BusinessModelTest(TestCase):
    def setUp(self):
        self.owner_group = Group.objects.create(name="Owner")
        self.specialist_group = Group.objects.create(name="Specialist")

        self.owner = UserFactory.create()
        self.owner_group.user_set.add(self.owner)

        self.business = BusinessFactory.create()

        self.specialist1 = UserFactory.create()
        self.specialist2 = UserFactory.create()
        self.specialist_group.user_set.add(self.specialist1)
        self.specialist_group.user_set.add(self.specialist2)

        self.position = PositionFactory.create()
        self.position.specialist.add(self.specialist2)
        self.business.position_set.add(self.position)

    def test_create_position_method(self):
        start_time, end_time = get_random_start_end_datetime()
        position = self.business.create_position(
            faker.word(), self.specialist1, start_time, end_time
        )
        all_positions = self.business.position_set.all()

        self.assertIn(position, all_positions)
        self.assertEqual(2, len(all_positions))

    def test_get_all_specialist_method(self):
        start_time, end_time = get_random_start_end_datetime()
        self.business.create_position(
            faker.word(), self.specialist1, start_time, end_time
        )
        all_specialists = self.business.get_all_specialists()

        self.assertIn(self.specialist1, all_specialists)
        self.assertIn(self.specialist2, all_specialists)
        self.assertEqual(2, len(all_specialists))
