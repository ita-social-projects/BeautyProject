#!/bin/bash

sudo rm -rf /etc/nginx/nginx.conf

sudo touch /etc/nginx/nginx.conf

sudo printf "" > /etc/nginx/nginx.conf

cd home
cd ec2-user
cd Beauty

python3.9 -m venv venv

source venv/bin/activate

pip3.9 install -r requirements.txt

# python3 manage.py makemigrations
# python3 manage.py migrate
# python3 manage.py collectstatic --noinput

# gunicorn beauty.wsgi:application --bind 0.0.0.0:8000
