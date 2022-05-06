from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, RegexValidator
from django.db import models, IntegrityError
from django.db.models import F, Subquery
from django.db.utils import DataError
from django.urls import reverse


ROLE_CHOICES = (
    (0, 'visitor'),
    (1, 'admin'),
)


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
    """
        This class represents a basic user. \n
        Attributes:
        -----------
        param first_name: Describes first name of the user
        type first_name: str max length=20
        param last_name: Describes last name of the user
        type last_name: str max length=20
        param patronymic: Describes middle name of the user
        type patronymic: str max length=20
        param email: Describes the email of the user
        type email: str, unique, max length=100
        param password: Describes the password of the user
        type password: str
        param created_at: Describes the date when the user was created. Can't be changed.
        type created_at: int (timestamp)
        param updated_at: Describes the date when the user was modified
        type updated_at: int (timestamp)
        param role: user role, default role (0, 'visitor')
        type updated_at: int (choices)
        param is_active: user role, default value False
        type updated_at: bool

    """

    ROLE_CHOICES = [
        (1, "Customer"),
        (2, "Owner"),
        (3, "Specialist")
    ]

    RE_PHONE_NUM = (r"^(?:\+38)?(?:\([0-9]{3}\)[ .-]?[0-9]{3}[ .-]?[0-9]{2}\
                    [ .-]?[0-9]{2}|[0-9]{3}[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?\
                    [0-9]{2}|[0-9]{3}[0-9]{7})$")
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(blank=True, max_length=20)
    patronymic = models.CharField(blank=True, max_length=20)
    email = models.EmailField(max_length=100, unique=True,
                              validators=(validate_email,))
    password = models.CharField(max_length=128)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    bio = models.TextField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True,
                                    validators=(
                                        RegexValidator(regex=RE_PHONE_NUM),))
    role = models.IntegerField(choices=ROLE_CHOICES, default=1)
    rating = models.IntegerField(blank=True, default=0)

    avatar = models.ImageField(blank=True)
    is_active = models.BooleanField(default=True)

    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('password', 'first_name')

    # patronymic = models.CharField(blank=True, max_length=20)
    # role = models.IntegerField(default=0, choices=ROLE_CHOICES)

    class Meta:
        ordering = ['id']

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    def __str__(self):
        """
        Magic method is redefined to show all information about CustomUser.
        :return: user id, user first_name, user patronymic, user last_name,
                 user email, user password, user updated_at, user created_at,
                 user role, user is_active
        """
        return str(self.to_dict())[1:-1]

    def __repr__(self):
        """
        This magic method is redefined to show class and id of CustomUser object.
        :return: class, id
        """
        return f'{self.__class__.__name__}(id={self.id})'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('authentication:user-books', kwargs={'id': self.id})


    @staticmethod
    def get_by_id(user_id):
        """
        :param user_id: SERIAL: the id of a user to be found in the DB
        :return: user object or None if a user with such ID does not exist
        """
        try:
            user = CustomUser.objects.get(id=user_id)
            return user
        except CustomUser.DoesNotExist:
            pass
            # LOGGER.error("User does not exist")

    @staticmethod
    def get_by_email(email):
        """
        Returns user by email
        :param email: email by which we need to find the user
        :type email: str
        :return: user object or None if a user with such ID does not exist
        """
        try:
            user = CustomUser.objects.get(email=email)
            return user
        except CustomUser.DoesNotExist:
            # LOGGER.error("User does not exist")
            pass

    @staticmethod
    def delete_by_id(user_id):
        """
        :param user_id: an id of a user to be deleted
        :type user_id: int
        :return: True if object existed in the db and was removed or False if it didn't exist
        """

        try:
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return True
        except CustomUser.DoesNotExist:
            # LOGGER.error("User does not exist")
            pass
        return False

    @staticmethod
    def create(email, password, first_name=None, patronymic=None, last_name=None):
        """
        :param first_name: first name of a user
        :type first_name: str
        :param patronymic: middle name of a user
        :type patronymic: str
        :param last_name: last name of a user
        :type last_name: str
        :param email: email of a user
        :type email: str
        :param password: password of a user
        :type password: str
        :return: a new user object which is also written into the DB
        """
        # print(validate_email("96mail.com"))
        data = {}
        data['first_name'] = first_name if first_name else ''
        data['last_name'] = last_name if last_name else ''
        data['patronymic'] = patronymic if patronymic else ''
        data['email'] = email
        user = CustomUser(**data)
        user.set_password(password)
        try:
            validate_email(user.email)
            user.save()
            return user
        except (IntegrityError, AttributeError, ValidationError, DataError):
            # LOGGER.error("Wrong attributes or relational integrity error")
            pass

    def to_dict(self):
        """
        :return: user id, user first_name, user patronymic, user last_name,
                 user email, user password, user updated_at, user created_at, user is_active
        :Example:
        | {
        |   'id': 8,
        |   'first_name': 'fn',
        |   'patronymic': 'mn',
        |   'last_name': 'ln',
        |   'email': 'ln@mail.com',
        |   'created_at': 1509393504,
        |   'updated_at': 1509402866,
        |   'role': 0
        |   'is_active:' True
        | }
        """

        return {
            'id': self.id,
            'first_name': self.first_name,
            'patronymic': self.patronymic,
            'last_name': self.last_name,
            'email': self.email,
            'created_at': int(self.created_at.timestamp()),
            'updated_at': int(self.updated_at.timestamp()),
            'role': self.role,
            'is_active': self.is_active}

    def update(self,
               first_name=None,
               last_name=None,
               patronymic=None,
               password=None,
               role=None,
               is_active=None):
        """
        Updates user profile in the database with the specified parameters.\n
        :param first_name: first name of a user
        :type first_name: str
        :param patronymic: middle name of a user
        :type patronymic: str
        :param last_name: last name of a user
        :type last_name: str
        :param password: password of a user
        :type password: str
        :param role: role id
        :type role: int
        :param is_active: activation state
        :type is_active: bool
        :return: None
        """

        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if patronymic:
            self.patronymic = patronymic
        if password:
            self.set_password(password)
        if role:
            self.role = role
        if is_active is not None:
            self.is_active = is_active
        self.save()

    @staticmethod
    def get_all():
        """
        returns data for json request with QuerySet of all users
        """
        all_users = CustomUser.objects.all()
        return all_users

    def get_role_name(self):
        """
        returns str role name
        """
        return self.get_role_display()
