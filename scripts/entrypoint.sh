#!/bin/sh

set -e

python manage.py collectstatic --noinput

gunicorn --bind :8000 --workers=4 beauty.wsgi:application
