from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from beauty import signals
        # Explicitly connect a signal handler.
        # signals.request_finished.connect(signals.my_callback)
