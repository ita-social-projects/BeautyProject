from collections import namedtuple

from django.utils import timezone
import factory
from api.models import *
from factory import fuzzy
from django.contrib.auth.models import Group


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group_{n}")

    @staticmethod
    def get_groups():
        groups_name = ['Admin', 'Customer', 'Owner', 'Specialist']
        GroupNamed = namedtuple("GroupNamed", list(map(lambda name: name.lower(), groups_name)))
        groups = GroupNamed(*[GroupFactory(name=name) for name in groups_name])
        return groups


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.LazyAttribute(lambda o: f'{o.first_name.lower()}'
                                            f'{o.phone_number[-2:]}@example.com')
    first_name = factory.Faker("first_name")
    phone_number = factory.Faker("phone_number")
    password = "1234567890"

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.groups.add(group)


class BusinessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Business

    name = factory.Sequence(lambda n: f"Business_{n}")
    type = factory.Sequence(lambda n: f"Business_type_#{n}")
    owner = factory.SubFactory(CustomUserFactory)
    address = factory.Faker("address")
    description = factory.Faker('sentence', nb_words=4)


class PositionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Position

    name = factory.Sequence(lambda n: f"Position_{n}")
    business = factory.SubFactory(BusinessFactory)
    start_time = factory.LazyFunction(timezone.now)
    end_time = factory.LazyAttribute(lambda o: o.start_time - timezone.timedelta(hours=8))

    @factory.post_generation
    def specialist(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for spec in extracted:
                self.specialist.add(spec)


class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Service

    position = factory.SubFactory(PositionFactory)
    name = factory.Sequence(lambda n: f"Service_{n}")
    price = fuzzy.FuzzyDecimal(10.0, 100.0)
    description = factory.Faker('sentence', nb_words=4)
    duration = fuzzy.FuzzyInteger(15, 60)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    status = fuzzy.FuzzyChoice(Order.StatusChoices, getter=lambda c: c[0])
    specialist = factory.SubFactory(CustomUserFactory)
    customer = factory.SubFactory(CustomUserFactory)
    service = factory.SubFactory(ServiceFactory)
    reason = ""
    start_time = factory.LazyFunction(timezone.now)
