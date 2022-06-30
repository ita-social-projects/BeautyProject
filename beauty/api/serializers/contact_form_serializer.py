"""This module with serializer for support contact form."""

import logging

from rest_framework import serializers


logger = logging.getLogger(__name__)


class ContactFormSerializer(serializers.Serializer):
    """Serializer for contact form fields."""
    name = serializers.CharField(max_length=50, allow_blank=False)
    email = serializers.EmailField(allow_blank=False)
    message = serializers.CharField(max_length=500, allow_blank=False)
