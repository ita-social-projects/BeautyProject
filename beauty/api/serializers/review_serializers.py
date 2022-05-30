"""The module includes serializers for Review model."""

from rest_framework import serializers
from api.models import Review

import logging

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