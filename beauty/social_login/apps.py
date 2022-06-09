"""Apps for social authorization."""

from django.apps import AppConfig


class SocialLoginConfig(AppConfig):
    """App configuration for Google authorization."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "social_login"
