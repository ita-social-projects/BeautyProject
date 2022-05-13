"""This module provides all needed models"""

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
from django.utils.translation import gettext as _

from beauty.utils import ModelsUtils


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
    """This class represents a custom User model

    Notes:
        Rating field could be negative, works like a rating system

    Attributes:
        first_name: First name of the user
        last_name: (optiomal) Last name of the user
        patronymic: (optiomal) Patronymic of the user
        email: Email of the user
        updated_at: Time of the last update
        created_at: Time when user was created
        bio: (optiomal) Additional information about user
        phone_number: Phone number of the user
        rating: Rating of the user (specialist group only)
        avatar: (optiomal) Avatar of the user
        is_active: Determines whether user account is active
        is_admin: Determines whether user is admin

    Properties:
        is_staff: Returns true if user is admin

    """

    first_name = models.CharField(
        max_length=20
    )
    last_name = models.CharField(
        blank=True,
        max_length=20
    )
    patronymic = models.CharField(
        blank=True,
        max_length=20
    )
    email = models.EmailField(
        max_length=100,
        unique=True,
        validators=(validate_email,)
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    bio = models.TextField(
        max_length=255,
        blank=True,
        null=True
    )
    phone_number = PhoneNumberField(
        unique=True
    )
    rating = models.IntegerField(
        blank=True,
        default=0
    )
    avatar = models.ImageField(
        blank=True,
        upload_to=ModelsUtils.upload_location
    )

    is_active = models.BooleanField(default=True)

    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('password', 'first_name', 'phone_number')

    class Meta:
        """This meta class stores verbose names ordering data"""
        ordering = ['id']
        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def is_staff(self):
        """Determines whether user is admin"""
        return self.is_admin

    def get_full_name(self):
        """Shows full name of the user"""
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        """str: Returns full name of the user"""
        return self.get_full_name()

    def __repr__(self):
        """str: Returns CustomUser name and its id"""
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

class Order(models.Model):
    """This class represents a basic Order (for an appointment system)
    that stores all the required information.

    Note:
        reason attribute is only neaded if order's status is cancelled
        end_time is autocalculated during creation, no need to put it

    Attributes:
        status: Status of the order
        start_time: Appointment time and date of the order
        end_time: Time that is calculated according to the duration of service
        created_at: Time of creation of the order
        specialist: An appointed specialist for the order
        customer: A customer who will recieve the order
        service: Service that will be fulfield for the order
        reason: (optional) Reason for cancellation
    
    Properties:
        is_active: Returns true if order's status is active
        is_approved: Returns true if order's status is approved
        is_declined: Returns true if order's status is declined

    """

    class StatusChoices(models.TextChoices):
        """This class is used for status codes"""
        ACTIVE = 0, _('Active')
        COMPLETED = 1, _('Completed')
        CANCELLED = 2, _('Cancelled')
        APPROVED = 3, _('Approved')
        DECLINED = 4, _('Declined')

    class Meta:
        """This meta class stores ordering and permissions data"""
        ordering = ['id']
        unique_together = ['specialist', 'customer']
        get_latest_by = "created_at"
        permissions = [
        ('can_add_order', 'Can add an order'),
        ('can_change_order', 'Can change an order'),
        ('can_set_status', 'Can set a status of the order'),
        ('can_view_order', 'Can view an order')
        ]
    
    status = models.CharField(
        max_length=2,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name=_('Current status')
    )
    start_time = models.DateTimeField(
        editable=True, 
        verbose_name=_('Appointment time')
    )
    end_time = models.DateTimeField(
        editable=False, 
        verbose_name=_('End time')
    )
    created_at = models.DateTimeField(
        auto_now=True, 
        editable=False, 
        verbose_name=_('Created at')
    )
    specialist = models.ForeignKey(
        'CustomUser',
        related_name = 'specialist_orders', 
        on_delete=models.CASCADE,
        verbose_name=_('Specialist')
    )
    customer = models.ForeignKey(
        'CustomUser', 
        related_name = 'customer_orders',
        on_delete=models.CASCADE,
        verbose_name=_('Customer')
    )
    service = models.ForeignKey(
        'Service', 
        on_delete=models.CASCADE,
        verbose_name=_('Service')
    )
    reason = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('Reason for cancellation')
    )

    def save(self, *args, **kwargs):
        """Reimplemented save method for end_time calculation"""
        from datetime import timedelta
        self.end_time = self.start_time + timedelta(minutes=self.service.duration)
        super(Order, self).save(*args, **kwargs)
        return self

    @property
    def is_active(self) -> bool:
        """bool: Returns true if order's status is active"""
        return self.status == self.StatusChoices.ACTIVE
    
    @property
    def is_approved(self) -> bool:
        """bool: Returns true if order's status is approved"""
        return self.status == self.StatusChoices.APPROVED

    @property
    def is_declined(self) -> bool:
        """bool: Returns true if order's status is declined"""
        return self.status == self.StatusChoices.DECLINED

    def mark_as_approved(self):
        """Marks order as approved"""
        self.status = self.StatusChoices.APPROVED
        self.save(update_fields=['status'])

    def mark_as_cancelled(self):
        """Marks order as cancelled"""
        self.status = self.StatusChoices.CANCELLED
        self.save(update_fields=['status'])

    def mark_as_completed(self):
        """Marks order as completed"""
        self.status = self.StatusChoices.COMPLETED
        self.save(update_fields=['status'])

    def mark_as_declined(self):
        """Marks order as declined"""
        self.status = self.StatusChoices.DECLINED
        self.save(update_fields=['status'])

    def add_reason(self, reason: str):
        """Add a reason for an order"""
        self.reason = reason
        self.save(update_fields=['reason'])
    
    def get_reason(self) -> str:
        """str: Returns a reason"""
        return self.reason
    
    def __str__(self) -> str:
        """str: Returns a verbose title of the order"""
        return f"Order #{self.id}"

    def __repr__(self) -> str:
        """str: Returns a string representation of the order"""
        return f"Order #{self.id} ({self.status})"
