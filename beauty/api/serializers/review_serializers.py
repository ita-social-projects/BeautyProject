"""The module includes serializers for Review model."""
import logging

from rest_framework import serializers
from api.models import Review

logger = logging.getLogger(__name__)


class ReviewDisplaySerializer(serializers.ModelSerializer):
    """This is a serializer for review display"""

    class Meta:
        """This is a class Meta that keeps settings for serializer"""

        model = Review
        fields = ("text_body",
                  "rating",
                  "from_user",
                  "to_user",
                  "date_of_publication")


class ReviewDisplayDetailSerializer(serializers.ModelSerializer):
    """Serializer to receive and update specific review"""

    class Meta:
        """This is a class Meta that keeps settings for serializer"""

        model = Review
        fields = ("text_body", "rating")

    def update(self, instance: object, validated_data: dict) -> object:
        """Update review information using dict with data.

        Args:
            instance (object): instance for changing
            validated_data (dict): validated data for updating instance

        Returns:
            review (object): instance with updated data

        """
        text_body = validated_data.get("text_body", None)
        if len(text_body) > 500:
            logger.info(
                f"Review with id {instance.id} was unsuccessfully updated")
            raise serializers.ValidationError(
                {"error": "Text body length must be under 500 symbols"}
            )

        logger.info(f"Data for review {instance} was updated")

        return super().update(instance, validated_data)
