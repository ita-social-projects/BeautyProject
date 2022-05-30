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
        fields = ("id",
                  "text_body",
                  "rating",
                  "from_user",
                  "to_user",
                  "date_of_publication")


class ReviewDisplayDetailSerializer(serializers.ModelSerializer):
    """Serializer to receive and update specific review"""

    class Meta:
        """This is a class Meta that keeps settings for serializer"""

        model = Review
        fields = ("id",
                  "text_body",
                  "rating",
                  "from_user",
                  "to_user",
                  "date_of_publication")

    def update(self, instance: object, validated_data: dict) -> object:
        """Update review information using dict with data.

        Args:
            instance (object): instance for changing
            validated_data (dict): validated data for updating instance

        Returns:
            review (object): instance with updated data

        """
        try:
            new_instance = super().update(instance, validated_data)
            return new_instance
        except Exception as e:
            logger.info(e.__str__())
            raise e
