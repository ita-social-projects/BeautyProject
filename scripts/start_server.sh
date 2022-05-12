#!/bin/bash

sudo rm -rf /etc/nginx/nginx.conf

sudo touch /etc/nginx/nginx.conf

sudo printf "" > /etc/nginx/nginx.conf

pwd

ls

cd var/www/Beauty/beauty

pwd

ls

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

gunicorn beauty.wsgi:application --bind 0.0.0.0:8000