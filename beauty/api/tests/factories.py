from django.contrib.auth import get_user_model

from random import randint
from datetime import datetime, timedelta

import factory
from factory.django import DjangoModelFactory
from faker import Factory, Faker

from api.models import Business, Position

User = get_user_model()
faker = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email', 'phone_number')

    @staticmethod
    def get_first_and_last_names():
        full_name = faker.name().split()
        first_name = full_name.pop(0)
        last_name = ' '.join(full_name)
        return first_name, last_name

    first_name, last_name = get_first_and_last_names()
    phone_number = faker.phone_number()
    email = faker.email()
    password = faker.password()


class BusinessFactory(DjangoModelFactory):
    class Meta:
        model = Business

    name = faker.word()
    type = faker.word()
    description = faker.text()
    owner = factory.SubFactory(UserFactory)


class PositionFactory(DjangoModelFactory):
    class Meta:
        model = Position

    @staticmethod
    def fake_start_end_datetime():
        start_time = datetime(
            2022, randint(1, 12), randint(1, 31), randint(1, 24)
        )
        return start_time, start_time + timedelta(hours=8)

    name = faker.word()
    business = factory.SubFactory(BusinessFactory)
    start_time, end_time = fake_start_end_datetime()
