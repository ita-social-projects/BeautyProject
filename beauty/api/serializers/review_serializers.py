"""The module includes serializers for Review model."""

from rest_framework import serializers
from api.models import Review

import logging

logger = logging.getLogger(__name__)


class ReviewDisplaySerializer(serializers.ModelSerializer):
    """This is a serializer for review display."""

    class Meta:
        """This is a class Meta that keeps settings for serializer."""

        model = Review
        fields = "__all__"


class ReviewAddSerializer(serializers.ModelSerializer):
    """This is a serializer for creating a Review."""

    class Meta:
        """This is a class Meta that keeps settings for serializer."""

        model = Review
        fields = ["text_body", "rating", "from_user", "to_user"]

    def save(self, **kwargs):
        """Method for saving reviews.

        The save method was redefined in order to check whether users
        are trying to review themselves, which is not allowed. It also
        checks that users are not trying to review a non specialists.
        """
        reviewer = kwargs["from_user"]
        reviewee = kwargs["to_user"]
        if reviewer == reviewee:
            logger.info(f"User {reviewer} (id = {reviewer.id}) tried reviewing himself or herself.")
            raise serializers.ValidationError(
                {"error": "You are not able to review yourself."},
            )
        if not reviewee.is_specialist:
            logger.info(f"User {reviewer} (id = {reviewer.id}) tried reviewing a non "
                        f"specialist user {reviewee} (id = {reviewee.id}).")
            raise serializers.ValidationError(
                {"error": "You are not able to review a nonspecialist."},
            )
        return super().save(**kwargs)
