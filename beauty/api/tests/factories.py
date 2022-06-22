"""Module for all factories classes used in the tests.

Todo:
    - fix addresses in Business factory
"""

from collections import namedtuple
import calendar
import random
from django.utils import timezone
from datetime import timedelta
from random import choice
import factory
from factory import fuzzy
from api.models import (CustomUser, Order, Service, Position, Business, Review)
from django.contrib.auth.models import Group


class RoundedTime:
    """Class with rounded time.

    Provide time with zero seconds and minutes multiplied by 5
    """

    minutes = (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55)

    @classmethod
    def calculate_rounded_time_minutes_seconds(cls):
        """Datetime rigth now with rounded time.

        Returns datetime.now() with edited minutes and seconds
        """
        return timezone.now().replace(
            minute=choice(cls.minutes), second=0, microsecond=0,
        )

    @classmethod
    def get_rounded_duration(cls):
        """Return timedelta with minutes multiplied by 5."""
        return timedelta(minutes=choice(cls.minutes))


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
    last_name = factory.Faker("last_name")
    phone_number = factory.Sequence(lambda n: "+38050666%04d" % n)
    password = factory.PostGenerationMethodCall("set_password", "1234567890")
    bio = factory.Faker("paragraph", nb_sentences=5)

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
    owner = factory.SubFactory(CustomUserFactory, is_active=True)
    address = factory.Faker("address")
    description = factory.Faker("sentence", nb_words=4)

    @factory.lazy_attribute
    def working_time(self):
        """Generates business working time."""
        start_hour = f"{random.randint(6, 10)}:{random.randint(0, 59)}"
        end_hour = f"{random.randint(13, 20)}:{random.randint(0, 59)}"
        week_days = [day.capitalize()
                     for day in calendar.HTMLCalendar.cssclasses]

        working_time = {day: [start_hour, end_hour]
                        if random.random() > 0.25
                        else []
                        for day in week_days}

        return working_time


class PositionFactory(factory.django.DjangoModelFactory):
    """Factory class for testing Position model."""

    class Meta:
        """Class Meta for the definition of the Position model."""

        model = Position

    name = factory.Sequence(lambda n: f"Position_{n}")
    business = factory.SubFactory(BusinessFactory)

    @factory.lazy_attribute
    def working_time(self):
        """Generates working time based on business."""
        working_time = self.business.working_time

        work_day = [key for key, value in working_time.items() if value][0]

        # If all days are weekends
        if not work_day:
            return working_time

        start_hour = [int(time)
                      for time in working_time[work_day][0].split(":")]
        end_hour = [int(time)
                    for time in working_time[work_day][1].split(":")]

        start_hour = f"{random.randint(start_hour[0], 11)}:"\
                     + f"{random.randint(start_hour[1], 59)}"
        end_hour = f"{random.randint(13, end_hour[0])}:"\
                   + f"{random.randint(0, end_hour[1])}"

        working_time = {day: [start_hour, end_hour]
                        if working_time[day]
                        else []
                        for day in working_time.keys()}

        return working_time

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
    duration = factory.LazyFunction(RoundedTime.get_rounded_duration)


class OrderFactory(factory.django.DjangoModelFactory):
    """Factory class for testing Order model."""

    class Meta:
        """Class Meta for the definition of the Order model."""

        model = Order

    status = fuzzy.FuzzyChoice(Order.StatusChoices, getter=lambda c: c.ACTIVE)
    specialist = factory.SubFactory(CustomUserFactory, is_active=True)
    customer = factory.SubFactory(CustomUserFactory, is_active=True)
    service = factory.SubFactory(ServiceFactory)
    reason = ""
    start_time = factory.LazyFunction(RoundedTime.calculate_rounded_time_minutes_seconds)


class ReviewFactory(factory.django.DjangoModelFactory):
    """Factory class for testing Review model."""

    class Meta:
        """Class Meta for the definition of the Review model."""
        model = Review

    text_body = factory.Faker("text", max_nb_chars=500)
    rating = factory.Faker("random_int", min=0, max=5)
