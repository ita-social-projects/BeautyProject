import factory
from faker import Factory

from django.contrib.auth import get_user_model
from api.models import Business


User = get_user_model()
faker = Factory.create()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

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


class BusinessFactory(factory.DjangoModelFactory):
    class Meta:
        model = Business

    name = faker.word()
    type = faker.word()
    description = faker.text()
    owner = factory.SubFactory(UserFactory)
