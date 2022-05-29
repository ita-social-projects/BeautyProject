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


class UserFactory():
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


class BusinessFactory():
    @classmethod
    def create(cls) -> Business:
        owner = UserFactory.create()
        owner_group = Group.objects.get_or_create(name="Owner")[0]
        owner_group.user_set.add(owner)

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


class PositionFactory():
    @classmethod
    def create(cls) -> Position:
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
