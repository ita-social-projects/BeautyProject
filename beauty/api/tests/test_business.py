from django.test import TestCase
from django.contrib.auth import get_user_model

from api.models import Business
from .factories import UserFactory, BusinessFactory

User = get_user_model()


class BusinessModelTest(TestCase):
    def setUp(self):
        self.owner1 = UserFactory.create()
        self.business1 = BusinessFactory.create()

    def test_
