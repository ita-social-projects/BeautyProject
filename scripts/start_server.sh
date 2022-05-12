#!/bin/bash

cd home
cd ec2-user
cd Beauty

sudo cp /home/ec2-user/www/project/nginx/default.conf /etc/nginx/nginx.conf

python3.9 -m venv venv

source venv/bin/activate

pip3.9 install -r requirements.txt

python3.9 manage.py makemigrations
python3.9 manage.py migrate
python3.9 manage.py collectstatic --noinput && python3.9 manage.py runserver 0.0.0.0:8000

gunicorn beauty.wsgi:application --bind 0.0.0.0:8000

systemctl start nginx
