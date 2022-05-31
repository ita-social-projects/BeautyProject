<<<<<<< HEAD
from email.headerregistry import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# import factory
# from factory.django import DjangoModelFactory
from faker import Faker

from api.models import Business, Position
from beauty.utils import get_random_start_end_datetime

User = get_user_model()
faker = Faker()


class UserFactory:
    @classmethod
    def create(cls) -> User:
        first_name, last_name = cls.get_first_last_names()

        return User.objects.create(
            first_name=first_name, last_name=last_name, bio=faker.text(),
            phone_number=faker.phone_number(), email=faker.email(),
            password=faker.password()
        )

    @staticmethod
    def get_first_last_names():
        full_name = faker.name().split()
        first_name = full_name.pop(0)
        return first_name, " ".join(full_name)

    @staticmethod
    def add_to_group(user, group_name):
        group = Group.objects.get_or_create(name=group_name)[0]
        group.user_set.add(user)


class OwnerFactory(UserFactory):
    @classmethod
    def create(cls) -> User:
        owner = super().create()
        cls.add_to_group(owner, "Owner")
        return owner


class ClientFactory(UserFactory):
    @classmethod
    def create(cls) -> User:
        client = super().create()
        cls.add_to_group(client, "Client")
        return client


class SpecialistFactory(UserFactory):
    @classmethod
    def create(cls) -> User:
        specialist = super().create()
        cls.add_to_group(specialist, "Specialist")
        return specialist


# class UserFactory(DjangoModelFactory):
#     class Meta:
#         model = User
#         django_get_or_create = ('email', 'phone_number')

#     @staticmethod
#     def get_first_last_names():
#         full_name = faker.name().split()
#         first_name = full_name.pop(0)
#         return first_name, " ".join(full_name)

#     first_name, last_name = get_first_last_names()
#     phone_number = faker.phone_number()
#     email = faker.email()
#     password = faker.password()


class BusinessFactory:
    @staticmethod
    def create() -> Business:
        owner = OwnerFactory.create()

        return Business.objects.create(
            name=faker.word(), type=faker.word(), 
            description=faker.text(), owner=owner
        )    


# class BusinessFactory(DjangoModelFactory):
#     class Meta:
#         model = Business

#     name = faker.word()
#     type = faker.word()
#     description = faker.text()
#     owner = factory.SubFactory(UserFactory)


class PositionFactory:
    @staticmethod
    def create() -> Position:
        business = BusinessFactory.create()
        start_time, end_time = get_random_start_end_datetime()

        return Position.objects.create(
            name=faker.word(), business=business, start_time=start_time, 
            end_time=end_time
        )


# class PositionFactory(DjangoModelFactory):
#     class Meta:
#         model = Position

#     name = faker.word()
#     business = factory.SubFactory(BusinessFactory)
#     start_time, end_time = get_random_start_end_datetime()
=======
"""Module for all factories classes used in the tests."""

from collections import namedtuple

from django.utils import timezone
import factory
from factory import fuzzy
from api.models import (CustomUser, Order, Service, Position, Business)
from django.contrib.auth.models import Group


class GroupFactory(factory.django.DjangoModelFactory):
    """Factory class for testing Group model."""

    class Meta:
        """Class Meta for the definition of the Group model."""

        model = Group

    name = factory.Sequence(lambda n: f"Group_{n}")

    @staticmethod
    def groups_for_test():
        """Get all existing groups from the project."""
        groups_name = ["Admin", "Customer", "Owner", "Specialist"]
        GroupNamed = namedtuple("GroupNamed", list(map(lambda name: name.lower(), groups_name)))
        groups = GroupNamed(*[GroupFactory(name=name) for name in groups_name])
        return groups


class CustomUserFactory(factory.django.DjangoModelFactory):
    """Factory class for testing CustomUser model."""

    class Meta:
        """Class Meta for the definition of the CustomUser model."""

        model = CustomUser

    email = factory.LazyAttribute(lambda o: f"{o.first_name.lower()}"
                                            f"{o.phone_number[-2:]}@example.com")
    first_name = factory.Faker("first_name")
    phone_number = factory.Faker("phone_number")
    password = "1234567890"

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """Get the field of ManyToMany for groups."""
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.groups.add(group)


class BusinessFactory(factory.django.DjangoModelFactory):
    """Factory class for testing Business model."""

    class Meta:
        """Class Meta for the definition of the Business model."""

        model = Business

    name = factory.Sequence(lambda n: f"Business_{n}")
    business_type = factory.Sequence(lambda n: f"Business_type_#{n}")
    owner = factory.SubFactory(CustomUserFactory)
    address = factory.Faker("address")
    description = factory.Faker("sentence", nb_words=4)


class PositionFactory(factory.django.DjangoModelFactory):
    """Factory class for testing Position model."""

    class Meta:
        """Class Meta for the definition of the Position model."""

        model = Position

    name = factory.Sequence(lambda n: f"Position_{n}")
    business = factory.SubFactory(BusinessFactory)
    start_time = factory.LazyFunction(timezone.now)
    end_time = factory.LazyAttribute(lambda o: o.start_time - timezone.timedelta(hours=8))

    @factory.post_generation
    def specialist(self, create, extracted, **kwargs):
        """Get the field of ManyToMany for specialist."""
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for spec in extracted:
                self.specialist.add(spec)


class ServiceFactory(factory.django.DjangoModelFactory):
    """Factory class for testing Service model."""

    class Meta:
        """Class Meta for the definition of the Service model."""

        model = Service

    position = factory.SubFactory(PositionFactory)
    name = factory.Sequence(lambda n: f"Service_{n}")
    price = fuzzy.FuzzyDecimal(10.0, 100.0)
    description = factory.Faker("sentence", nb_words=4)
    duration = fuzzy.FuzzyInteger(15, 60)


class OrderFactory(factory.django.DjangoModelFactory):
    """Factory class for testing Order model."""

    class Meta:
        """Class Meta for the definition of the Order model."""

        model = Order

    status = fuzzy.FuzzyChoice(Order.StatusChoices, getter=lambda c: c.ACTIVE)
    specialist = factory.SubFactory(CustomUserFactory)
    customer = factory.SubFactory(CustomUserFactory)
    service = factory.SubFactory(ServiceFactory)
    reason = ""
    start_time = factory.LazyFunction(timezone.now)
>>>>>>> 5410e2a0ddf326628e0a678a13662adb63338500
