"""The module includes serializers for Review model."""

from rest_framework import serializers
from api.models import Review


class ReviewAddSerializer(serializers.ModelSerializer):
    """This is a serializer for creating a Review"""

    text_body = serializers.CharField(max_length=500)
    rating = serializers.IntegerField(min_value=0, max_value=5)

    class Meta:
        """This is a class Meta that keeps settings for serializer"""
        model = Review
        fields = ['text_body', 'rating', 'from_user', 'to_user']

    def update(self, instance, validated_data):
        """This method is used in order to update/edit a review"""
        instance.text_body = validated_data.get(
            'text_body',
            instance.text_body
        )
        instance.rating = validated_data.get(
            'rating',
            instance.rating
        )
        instance.save()
        return instance

    def save(self, **kwargs):
        """The save method was redefined in order to check whether users
        are trying to review themselves, which is not allowed.
        """
        if kwargs['from_user'] == kwargs['to_user']:
            raise serializers.ValidationError(
                {'error': 'You are not able to review yourself'}
            )
        return super().save(**kwargs)
