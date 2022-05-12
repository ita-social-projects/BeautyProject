from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

from api.models import CustomUser


class PasswordsValidation(serializers.Serializer):

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError({"password": "Password confirmation does not match."})
        elif any([password, confirm_password]):
            raise serializers.ValidationError({"confirm_password": "Didn`t enter the password confirmation."})

        return super().validate(data)


class GroupListingField(serializers.RelatedField):

    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        return self.get_queryset().get(name=data).id


class CustomUserSerializer(PasswordsValidation, serializers.HyperlinkedModelSerializer):
    queryset = Group.objects.all()

    url = serializers.HyperlinkedIdentityField(view_name='api:user-detail', lookup_field='pk')

    password = serializers.CharField(write_only=True, required=True,
                                     style={'input_type': 'password', 'placeholder': 'Password'},
                                     validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True,
                                             style={'input_type': 'password',
                                                    'placeholder': 'Confirmation Password'})
    groups = GroupListingField(many=True, required=False, queryset=queryset)

    class Meta:
        model = CustomUser
        fields = ['url', 'id', 'email', 'first_name', 'patronymic', 'last_name',
                  'phone_number', 'bio', 'rating', 'avatar', 'groups', 'is_active', 'password', 'confirm_password']

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomUserDetailSerializer(PasswordsValidation, serializers.ModelSerializer):
    # orders = CustomerHyperlink(many=True, read_only=True)
    groups = GroupListingField(many=True, queryset=Group.objects.all())
    password = serializers.CharField(write_only=True, allow_blank=True, validators=[validate_password],
                                     style={'input_type': 'password', 'placeholder': 'New Password'})

    confirm_password = serializers.CharField(write_only=True, allow_blank=True,
                                             help_text='Leave empty if no change needed',
                                             style={'input_type': 'password',
                                                    'placeholder': 'Confirmation Password'})

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'patronymic', 'last_name',
                  'phone_number', 'bio', 'rating', 'avatar', 'groups', 'is_active', 'password', 'confirm_password']

    def update(self, instance, validated_data):
        confirm_password = validated_data.pop('confirm_password')
        if confirm_password:
            validated_data['password'] = make_password(confirm_password)
        return super().update(instance, validated_data)
