"""Module for api config."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Api config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        """Implicitly connect a signal handlers decorated with @receiver."""
        from beauty import signals
