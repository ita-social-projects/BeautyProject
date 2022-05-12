#!/bin/bash

sudo yum update -y

sudo yum install gcc libc-dev linux-headers postgresql-dev postgresql-client

sudo pip3 install -r requirements.txt 

sudo yum install -y nginx
