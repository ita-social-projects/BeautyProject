from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth.hashers import make_password

from api.models import CustomUser


# class CustomerHyperlink(serializers.HyperlinkedRelatedField):
#     view_name = 'authentication:user-order-detail'
#
#     def get_url(self, obj, view_name, request, format):
#         url_kwargs = {
#             'user_id': obj.user.pk,
#             'id': obj.pk
#         }
#         return reverse(view_name, kwargs=url_kwargs, request=request, format=format)
#
#     def get_object(self, view_name, view_args, view_kwargs):
#         lookup_kwargs = {
#             'user_id': view_kwargs['user_id'],
#             'id': view_kwargs['id']
#         }
#         return self.get_queryset().get(**lookup_kwargs)


class GroupListingField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name


class CustomUserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:user-detail', lookup_field='pk')

    password = serializers.CharField(write_only=True, required=True, help_text='Leave empty if no change needed',
                                     style={'input_type': 'password', 'placeholder': 'Password'},
                                     validators=[validate_password])
    groups = GroupListingField(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['url', 'id', 'email', 'first_name', 'patronymic', 'last_name',
                  'phone_number', 'bio', 'rating', 'avatar', 'groups', 'is_active', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomUserDetailSerializer(serializers.ModelSerializer):
    # orders = CustomerHyperlink(many=True, read_only=True)
    groups = GroupListingField(many=True, read_only=True)
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

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError({"password": "Password confirmation does not match."})
        elif any([password, confirm_password]):
            raise serializers.ValidationError({"confirm_password": "Didn`t enter the password confirmation."})

        return super().validate(data)

    def update(self, instance, validated_data):
        confirm_password = validated_data.pop('confirm_password')
        if confirm_password:
            validated_data['password'] = make_password(confirm_password)
        return super().update(instance, validated_data)

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     groups_name = Group.objects.filter(id__in=representation['groups']).values_list("name", flat=True)
    #     representation['groups'] = groups_name
    #     return representation


# class UserOrderDetailSerializer(serializers.HyperlinkedModelSerializer):
#     book = serializers.SlugRelatedField(read_only=True, slug_field='name')
#     user = serializers.CharField(source='user.get_full_name')
#
#     url = serializers.HyperlinkedIdentityField(view_name='order:order-detail', lookup_field='pk')
#
#     class Meta:
#         model = Order
#         fields = ['url', 'id', 'user', 'book', 'created_at', 'end_at', 'plated_end_at']
