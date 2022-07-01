"""Module for Celery app configuration."""

import os
import ssl
from celery import Celery
from django.conf import settings

# set the default Django settings module for the "celery" program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beauty.settings")
app = Celery("beauty",
             broker_use_ssl={
                 "ssl_cert_reqs": ssl.CERT_NONE,
             },
             redis_backend_use_ssl={
                 "ssl_cert_reqs": ssl.CERT_NONE,
             })

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
