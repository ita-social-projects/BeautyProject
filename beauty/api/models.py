"""This module provides all needed models"""

from datetime import timedelta
from address.models import AddressField
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import validate_email, MinValueValidator,\
    MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.utils.translation import gettext as _
from dbview.models import DbView
from beauty.utils import ModelsUtils


class MyUserManager(BaseUserManager):
    """This class provides tools for
     creating and managing CustomUser model
    """

    def create_user(self, email: str, first_name: str, password=None,
                    is_active=True, bio=None, **additional_fields):
        """
        Creates and saves CustomUser user instance with given fields values
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

    def create_superuser(self, email: str, first_name: str,
                         password=None, bio=None, **additional_fields):
        """Creates and saves CustomUser superuser
         instance with given fields values
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

        first_name (str): First name of the user
        last_name (str, optional): Last name of the user
        patronymic (str, optional): Patronymic of the user
        email (str): Email of the user
        updated_at (datetime): Time of the last update
        created_at (datetime): Time when user was created
        bio (str, optional): Additional information about user
        phone_number (str): Phone number of the user
        rating (int): Rating of the user (specialist group only)
        avatar (image, optional): Avatar of the user
        is_active (bool): Determines whether user account is active
        is_admin (bool): Determines whether user is admin

    Properties:

        is_staff (bool): Returns true if user is admin

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
        default='default_avatar.jpeg',
        upload_to=ModelsUtils.upload_location
    )

    is_active = models.BooleanField(default=False)

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


class Business(models.Model):
    """This class represents a Business model.
    
    Attributes:

        name (str): Name of business
        type (str): Type of business
        logo (image): Photo of business
        owner (CustomUser): Owner of business
        address (AddressField): Location of business
        description (str): Description of business
        created_at (datetime): Time when business was created

    """

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=20
    )
    type = models.CharField(
        verbose_name=_('Type'),
        max_length=100
    )
    logo = models.ImageField(
        upload_to=ModelsUtils.upload_location,
        blank=True
    )
    owner = models.ForeignKey(
        'CustomUser', 
        verbose_name=_('Owner'),
        on_delete=models.PROTECT, 
        related_name='businesses'
    )
    address = AddressField(
        verbose_name=_("Location"), 
        max_length=500,
        blank=True,
        null=True
    )
    description = models.CharField(
        verbose_name=_('Description'),
        max_length=255
    )
    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True
    )

    class Meta:
        """This meta class stores verbose names"""
        
        ordering = ['type']
        verbose_name = _('Business')
        verbose_name_plural = _('Businesses')

    def __str__(self) -> str:
        """str: Returns a verbose title of the business"""
        return str(self.name)

    #TODO: methods: get_all_specialist & create_position
    # def create_position(self, name, type, logo, owner, description):
    #     pos = Position(name=name)
    #     pos.save()

    def get_all_specialist(self):
        """"""
        specialists = [position.specialists.all() for position in self.positions.all()]
        return specialists


class WorkingTime(DbView):
    """
    This class represents Working time entity

    Attributes:

        block (bool): is free or not
        date (datetime): working day
        specialist (CustomUser): specialist id
        order (Order): order id

    """

    block = models.BooleanField(
        default=False,
        verbose_name=_("Is block")
    )
    date = models.DateTimeField(
        verbose_name=_("Working day")
    )

    specialist = models.ForeignKey(
        "CustomUser",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Specialist")
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.DO_NOTHING,
        verbose_name=_("Order")
    )

    @classmethod
    def view(cls):
        """Return string of our request"""
        #TODO: add request when all class will be realized
        req = ()
        return str(req.query)

    def __str__(self):
        """Magic method is redefined to show is this time blocked or no"""
        return self.block

    class Meta:
        """This meta class stores verbose names and permissions"""

        managed = False
        verbose_name = _("WorkingTime")
        verbose_name_plural = _("WorkingTimes")


class Position(models.Model):
    """This class represents position in Business

    Attributes:

        name (str): position name
        specialist (CustomUser): specialist id
        business (Business): business id
        start_time (datetime): specialist work starts at
        end_time (datetime): specialist work ends at

    """

    name = models.CharField(
        max_length=40,
        verbose_name= _("Name")
    )
    specialist = models.ManyToManyField(
        "CustomUser",
        verbose_name= _("Specialist"),
    )
    business = models.ForeignKey(
        "Business", 
        on_delete=models.CASCADE,
        verbose_name= _("Business")
    )
    start_time = models.DateTimeField(
        editable=True,
        verbose_name= _("Start time")
    )
    end_time = models.DateTimeField(
        editable=True,
        verbose_name= _("End time")
    )

    def __str__(self):
        """str: Returns name of Position"""
        return self.name

    class Meta:
        """This meta class stores verbose names and ordering data"""
        
        ordering = ['name']
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")


class Review(models.Model):
    """This class represents basic Review (for Reviews system)
    that stores all the required information.

    Attributes:

        text_body (str): body of the review
        rating (int): Rating of review(natural number from 1 to 5)
        date_of_publication (datetime): Date and time of review publication
        from_user (CustomUser): Foreign key, that determines Customer, who sent a review
        to_user (CustomUser): Foreign key, that determines Specialist, who must have
                 received review

    """

    text_body = models.CharField(
        max_length=500,
        verbose_name=_("Review text")
    )
    rating = models.IntegerField(
        blank=False,
        validators=(MinValueValidator(0), MaxValueValidator(5)),
        verbose_name=_("Review rating")
    )
    date_of_publication = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Time of review publication")
    )
    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name=_("Customer")
    )
    to_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name=_("Specialist")
    )

    def __str__(self):
        """str: Returns a verbose title of the review"""
        return self.text_body

    class Meta:
        """This meta class stores verbose names and permissions data"""

        ordering = ["date_of_publication"]
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")


class Order(models.Model):
    """This class represents a basic Order (for an appointment system)
    that stores all the required information.

    Note:
        reason attribute is only neaded if order's status is cancelled
        end_time is autocalculated during creation, no need to put it

    Attributes:

        status (TextChoices): Status of the order
        start_time (datetime): Appointment time and date of the order
        end_time (datetime): Time that is calculated according to the duration of service
        created_at (datetime): Time of creation of the order
        specialist (CustomUser): An appointed specialist for the order
        customer (CustomUser): A customer who will recieve the order
        service (Service): Service that will be fulfield for the order
        reason (str, optional): Reason for cancellation

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


class Service(models.Model):
    """This class represents a Service that can be provided by Specialist.

    Attributes:

        position (Position): Position that provides a service
        name (str): Name of the service
        price (decimal): Price of the service
        description (str): Description of the service
        duration (int): The time during which service is provided

    """

    position = models.ForeignKey(
        "Position",
        on_delete=models.CASCADE,
        verbose_name= _("Position")
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_("Service name")
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Service price")
    )
    description = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_("Service description")
    )
    duration = models.IntegerField(
        blank=False,
        verbose_name=_("Service duration")
    )

    def __str__(self):
        """str: Returns a verbose name of the service"""
        return self.name

    class Meta:

        """This meta class stores ordering and verbose name"""
        ordering = ['id']
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
