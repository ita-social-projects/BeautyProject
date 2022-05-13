import datetime
import os

from address.models import AddressField
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import validate_email, MinValueValidator,\
    MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models


def upload_location(instance, filename):
    new_name = instance.id if instance.id else instance.__class__.objects.all().last().id + 1
    new_path = os.path.join('upload', f"{new_name}.{filename.split('.')[-1]}")
    path = os.path.join(os.path.split(instance.avatar.path)[0], new_path)
    if os.path.exists(path):
        os.remove(path)
    return new_path


class MyUserManager(BaseUserManager):
    """User manager"""

    def create_user(self, email, first_name, password=None,
                    is_active=True, bio=None, **additional_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            is_active=is_active,
            bio=bio,
            **additional_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name,
                         password=None, bio=None, **additional_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, first_name,
                                password, bio=bio, **additional_fields)
        user.is_admin = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class CustomUser(PermissionsMixin, AbstractBaseUser):
    """This class represents a basic user."""

    first_name = models.CharField(max_length=20)
    last_name = models.CharField(blank=True, max_length=20)
    patronymic = models.CharField(blank=True, max_length=20)
    email = models.EmailField(max_length=100, unique=True,
                              validators=(validate_email,))
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    bio = models.TextField(max_length=255, blank=True, null=True)
    phone_number = PhoneNumberField(unique=True)
    rating = models.IntegerField(blank=True, default=0)
    avatar = models.ImageField(blank=True, upload_to=upload_location)

    is_active = models.BooleanField(default=True)

    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('password', 'first_name', 'phone_number')

    class Meta:
        ordering = ['id']

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        """
        Magic method is redefined to show all information about CustomUser.
        :return: user id, user first_name, user patronymic, user last_name,
                 user email, user password, user updated_at, user created_at,
                 user role, user is_active
        """
        return self.get_full_name()

    def __repr__(self):
        """
        This magic method is redefined to show class and id of CustomUser object.
        :return: class, id
        """
        return f'{self.__class__.__name__}(id={self.id})'


class Review(models.Model):
    """This class represents basic Review (for Reviews system)
    that stores all the required information.
    Attributes:
        text_body: body of the review
        rating: Rating of review(natural number from 1 to 5)
        date_of_publication: Date and time of review publication
        from_user: Foreign key, that determines Customer, who sent a review
        to_user: Foreign key, that determines Specialist, who must have
                 received review
    """

    text_body = models.CharField(
        max_length=500,
        verbose_name="Review text"
    )
    rating = models.IntegerField(
        blank=False,
        validators=(MinValueValidator(0), MaxValueValidator(5)),
        verbose_name="Review rating"
    )
    date_of_publication = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Time of review publication"
    )
    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name="FromRev"
    )
    to_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name="ToRev"
    )

    def __str__(self):
        """str: Returns a verbose title of the review"""
        return self.text_body

    class Meta:
        """This meta class stores verbose names and permissions data"""

        ordering = ["date_of_publication"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"


class Business(models.Model):

    address = AddressField(verbose_name="Location", max_length=500)

