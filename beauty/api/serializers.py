"""The module includes serializers for all project models."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from rest_framework.reverse import reverse

# from api.models import (CustomUser, Order)
from api.models import CustomUser

group_queryset = Group.objects.all()


# class CustomerHyperlink(serializers.HyperlinkedRelatedField):
#     view_name = 'api:user-order-detail'
#
#     def get_url(self, obj, view_name, request, format):
#
#         # url_kwargs = {
#         #     'user_id': obj.user.pk,
#         #     'id': obj.pk
#         # }
#         try:
#             obj_pk = obj.specialist.pk
#         except:
#             obj_pk = obj.customer.pk
#
#         url_kwargs = {
#             'user_id': obj_pk,
#             'id': obj.pk
#         }
#         return reverse(
#             view_name, kwargs=url_kwargs, request=request, format=format
#         )
#
#     def get_object(self, view_name, view_args, view_kwargs):
#         lookup_kwargs = {
#             'user_id': view_kwargs['user_id'],
#             'id': view_kwargs['id']
#         }
#         return self.get_queryset().get(**lookup_kwargs)


class PasswordsValidation(serializers.Serializer):
    """Validator for passwords."""

    def validate(self, data: dict) -> dict:
        """Validate password and password confirmation.

        Args:
            data (dict): dictionary with data for user creation

        Returns:
            data (dict): dictionary with validated data for user creation

        """
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError(
                    {"password": "Password confirmation does not match."})
        elif any([password, confirm_password]):
            raise serializers.ValidationError(
             {"confirm_password": "Didn`t enter the password confirmation."})

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
        return value.name

    def to_internal_value(self, data: str) -> int:
        """Reload lookup key from id to name of the instance.

        Args:
            data (str): lookup key (instance name)

        Returns:
            id (int): instance id

        """
        return self.get_queryset().get(name=data).id


class CustomUserSerializer(PasswordsValidation,
                           serializers.HyperlinkedModelSerializer):
    """Serializer for getting all users and creating a new user."""

    url = serializers.HyperlinkedIdentityField(
        view_name='api:user-detail', lookup_field='pk'
    )

    password = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password', 'placeholder': 'Password'},
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password',
               'placeholder': 'Confirmation Password'}
    )
    groups = GroupListingField(
        many=True, required=False, queryset=group_queryset
    )
    # orders = CustomerHyperlink(many=True, read_only=True)

    class Meta:
        """Class with a model and model fields for serialization."""

        model = CustomUser
        fields = ['url', 'id', 'email', 'first_name', 'patronymic',
                  'last_name', 'phone_number', 'bio', 'rating', 'avatar',
                  'is_active', 'groups', 'password',
                  'confirm_password']

    def create(self, validated_data: dict) -> object:
        """Create a new user using dict with data.

        Args:
            validated_data (dict): validated data for new user creation

        Returns:
            user (object): new user

        """
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomUserDetailSerializer(PasswordsValidation,
                                 serializers.ModelSerializer):
    """Serializer for getting and updating a concreted user."""

    # orders = CustomerHyperlink(many=True, read_only=True)
    groups = GroupListingField(many=True, queryset=group_queryset)
    password = serializers.CharField(
        write_only=True, allow_blank=True, validators=[validate_password],
        style={'input_type': 'password', 'placeholder': 'New Password'}
    )

    confirm_password = serializers.CharField(
        write_only=True, allow_blank=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password',
               'placeholder': 'Confirmation Password'}
    )

    class Meta:
        """Class with a model and model fields for serialization."""

        model = CustomUser
        fields = ['id', 'email', 'first_name', 'patronymic', 'last_name',
                  'phone_number', 'bio', 'rating', 'avatar', 'is_active',
                  'groups', 'password', 'confirm_password']

    def update(self, instance: object, validated_data: dict) -> object:
        """Update user information using dict with data.

        Args:
            instance (object): instance for changing
            validated_data (dict): validated data for updating instance

        Returns:
            user (object): instance with updated data

        """
        confirm_password = validated_data.pop('confirm_password')
        if confirm_password:
            validated_data['password'] = make_password(confirm_password)
        return super().update(instance, validated_data)


# class UserOrderDetailSerializer(serializers.HyperlinkedModelSqerializer):
#     # book = serializers.SlugRelatedField(read_only=True, slug_field='name')
#     # customer = serializers.CharField(source='user.get_full_name')
#
#     class Meta:
#         model = Order
#         fields = ['id', 'customer']
