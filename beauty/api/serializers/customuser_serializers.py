"""The module includes serializers for CustomUser model."""

import logging
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.reverse import reverse

from api.models import CustomUser
from beauty.tokens import OrderApprovingTokenGenerator
from beauty.utils import order_approve_decline_urls

logger = logging.getLogger(__name__)

group_queryset = Group.objects.all()


class OrderUserHyperlink(serializers.HyperlinkedRelatedField):
    """Custom HyperlinkedRelatedField for user orders."""

    view_name = "api:user-order-detail"
    url_user_id = "specialist_id"

    def __init__(self, **kwargs):
        """Init for OrderUserHyperlink."""
        self.view_name = kwargs.pop("view_name", self.view_name)
        self.url_user_id = kwargs.pop("url_user_id", self.url_user_id)
        super().__init__(**kwargs)

    def get_url(self, obj: object, view_name: str, request: dict, format_: str) -> str:
        """Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.

        Returns:
            url (str):  hyperlinks to the object

        """
        url_kwargs = {
            "user": getattr(obj, self.url_user_id),
            "pk": obj.pk,
        }

        url = reverse(
            view_name, kwargs=url_kwargs, request=request, format=format_,
        )

        logger.debug(f"User order url: {url} was added to "
                     f"user with id={getattr(obj, self.url_user_id)}")
        return url

    def to_representation(self, order):
        """Get order custom data for specialists.

        Args:
            order (Order): instance Order class

        Returns:
            data: dict or string for representation
        """
        url = super().to_representation(order)
        request = self.context.get("request")
        valid_token = OrderApprovingTokenGenerator().check_token(order, order.token)
        if all([request.user.is_authenticated, request.user == order.specialist, valid_token,
                self.url_user_id == "specialist_id"]):
            return {"url": url} | order_approve_decline_urls(order, request=request)
        return url


class PasswordsValidation(serializers.Serializer):
    """Validator for passwords."""

    def validate(self, data: dict) -> dict:
        """Validate password and password confirmation.

        Args:
            data (dict): dictionary with data for user creation

        Returns:
            data (dict): dictionary with validated data for user creation

        """
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        if password and confirm_password:
            if password != confirm_password:
                logger.info("Password: Password confirmation does not match")

                raise serializers.ValidationError(
                    {"password": "Password confirmation does not match."},
                )
        elif any([password, confirm_password]):

            logger.info("Password: One of the password fields is empty")

            raise serializers.ValidationError(
                {"confirm_password": "Didn`t enter the password confirmation."},
            )

        logger.info("Password and Confirm password is checked")

        return super().validate(data)


class GroupListingField(serializers.RelatedField):
    """The custom field for user groups."""

    def to_representation(self, value: object) -> str:
        """Change representation of instance from id to name.

        Args:
            value (object): instance of group

        Returns:
            object.name (str): attribute-name of an instance
        """
        logger.debug(f"Changed group representation from id={value.id}"
                     f" to name={value.name}")

        return value.name

    def to_internal_value(self, data: str) -> int:
        """Reload lookup key from id to name of the instance.

        Args:
            data (str): lookup key (instance name)

        Returns:
            id (int): instance id
        """
        logger.debug(f"Changed group lookup from name={data} to id")

        return self.get_queryset().get(name=data).id


class CustomUserSerializer(PasswordsValidation,
                           serializers.HyperlinkedModelSerializer):
    """Serializer for getting all users and creating a new user."""

    url = serializers.HyperlinkedIdentityField(
        view_name="api:user-detail", lookup_field="pk",
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password", "placeholder": "Password"},
        validators=[validate_password],
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password",
               "placeholder": "Confirmation Password",
               },
    )
    groups = GroupListingField(
        many=True,
        required=False,
        queryset=group_queryset,
    )
    specialist_orders = OrderUserHyperlink(many=True, read_only=True)
    customer_orders = OrderUserHyperlink(
        many=True,
        read_only=True,
        url_user_id="customer_id",
    )

    class Meta:
        """Class with a model and model fields for serialization."""

        model = CustomUser
        fields = ["url", "id", "email", "first_name", "patronymic",
                  "last_name", "phone_number", "bio", "rating", "avatar",
                  "is_active", "groups", "specialist_orders",
                  "customer_orders", "password", "confirm_password"]

    def create(self, validated_data: dict) -> object:
        """Create a new user using dict with data.

        Args:
            validated_data (dict): validated data for new user creation

        Returns:
            user (object): new user

        """
        confirm_password = validated_data.pop("confirm_password")
        validated_data["password"] = make_password(confirm_password)

        logger.info(f"User {validated_data['first_name']} with"
                    f" {validated_data['email']} was created.")

        return super().create(validated_data)

    def to_representation(self, instance):
        """Hide concrete specialist's orders from everybody.

        Args:
            instance (CustomUser): instance CustomUser class

        Returns:
            data (dict): data for representation
        """
        data = super().to_representation(instance)
        if not instance.is_specialist or self.context.get("request").user != instance:
            del data["specialist_orders"]
        return data


class CustomUserDetailSerializer(PasswordsValidation,
                                 serializers.ModelSerializer):
    """Serializer to receive and update a specific user."""

    groups = GroupListingField(many=True, queryset=group_queryset)
    password = serializers.CharField(
        write_only=True,
        allow_blank=True,
        validators=[validate_password],
        style={"input_type": "password", "placeholder": "New Password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        allow_blank=True,
        help_text="Leave empty if no change needed",
        style={
            "input_type": "password",
            "placeholder": "Confirmation Password",
        },
    )
    customer_exist_orders = OrderUserHyperlink(
        many=True,
        read_only=True,
        url_user_id="customer_id",
    )
    customer_reviews = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="api:review-detail",
        read_only=True,
    )

    class Meta:
        """Class with a model and model fields for serialization."""

        model = CustomUser
        fields = ["id", "email", "first_name", "patronymic", "last_name",
                  "phone_number", "bio", "rating", "avatar", "is_active",
                  "groups", "customer_exist_orders", "password",
                  "confirm_password", "customer_reviews"]

    def update(self, instance: object, validated_data: dict) -> object:
        """Update user information using dict with data.

        Args:
            instance (object): instance for changing
            validated_data (dict): validated data for updating instance

        Returns:
            user (object): instance with updated data

        """
        confirm_password = validated_data.get("confirm_password", None)
        if confirm_password:
            validated_data["password"] = make_password(confirm_password)
        else:

            validated_data["password"] = instance.password

        logger.info(f"Data for user {instance} was updated")

        return super().update(instance, validated_data)


class SpecialistInformationSerializer(CustomUserDetailSerializer):
    """Class for serializing specialist's information for specialist."""

    specialist_exist_orders = OrderUserHyperlink(many=True, read_only=True)
    specialist_reviews = serializers.URLField(
        default="",
    )

    class Meta(CustomUserDetailSerializer.Meta):
        """Meta class for SpecialistInformationdSerializer."""

        fields = CustomUserDetailSerializer.Meta.fields + ["specialist_exist_orders",
                                                           "specialist_reviews"]

    def to_representation(self, instance):
        """Method for representing an URL for displaying reviews."""
        data = super().to_representation(instance)

        data["specialist_reviews"] = reverse(
            "api:review-get",
            kwargs={"to_user": self.instance.id},
            request=self.context.get("request"),
        )

        logger.info(f"Data to display for specialist {instance} was updated")

        return data


class SpecialistDetailSerializer(serializers.ModelSerializer):
    """Class for serializing specialist's information for customer."""

    specialist_reviews = serializers.URLField(
        default="",
    )
    make_order = serializers.URLField(
        default="",
    )

    class Meta:
        """Meta class for SpecialistDetailSerializer."""

        model = CustomUser
        fields = ["id", "first_name", "patronymic", "last_name", "bio",
                  "rating", "avatar", "specialist_reviews", "make_order"]

    def to_representation(self, instance):
        """Method for representing an URL for making an order and for displaying reviews."""
        data = super().to_representation(instance)

        data["specialist_reviews"] = reverse(
            "api:review-get",
            kwargs={"to_user": self.instance.id},
            request=self.context.get("request"),
        )
        data["make_order"] = reverse(
            "api:order-create",
            request=self.context.get("request"),
        )

        logger.info(f"Data to display for specialist {instance} was updated")

        return data


class ResetPasswordSerializer(PasswordsValidation):
    """Serilizer for reseting password."""

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password", "placeholder": "New Password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={
            "input_type": "password",
            "placeholder": "Confirmation Password",
        },
    )

    class Meta:
        """Meta class for ResetPasswordSerializer."""

        model = CustomUser
        fields = ("password", "confirm_password")

    def validate(self, data: dict) -> dict:
        """Password validation."""
        if all([data.get("password"), data.get("confirm_password")]):

            logger.info("Password was reset")

            return super().validate(data)
        else:

            logger.info("Password: Fields should be valid")

            raise serializers.ValidationError(
                {"password": "Fields should be valid"},
            )


class InviteUserCreate(PasswordsValidation, serializers.ModelSerializer):
    """This serializer is used when user is registered by an invite link."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password", "placeholder": "Password"},
        validators=[validate_password],
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password",
               "placeholder": "Confirmation Password",
               },
    )

    class Meta:
        """Class with a model and model fields for serialization."""
        model = CustomUser
        fields = ("id", "first_name", "patronymic", "last_name",
                  "phone_number", "bio", "avatar",
                  "password", "confirm_password")

    def create(self, validated_data: dict) -> object:
        """Create a new user using dict with data.

        Args:
            validated_data (dict): validated data for new user creation

        Returns:
            user (object): new user

        """
        confirm_password = validated_data.pop("confirm_password")
        validated_data["password"] = make_password(confirm_password)

        logger.info(f"User {validated_data['first_name']} with"
                    f" {validated_data['email']} was created.")

        return super().create(validated_data)
