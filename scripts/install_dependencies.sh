#!/bin/bash

sudo yum update -y

# sudo yum install gcc libc-dev linux-headers postgresql-dev \ 
#                  postgresql-client libpq-dev python3-dev \
#                  python-setuptools python-devel postgresql-devel

yum install -y python-psycopg2 postgresql libncurses5-dev libffi libffi-devel libxml2-devel libxslt-devel libxslt1-dev
yum install -y postgresql-libs postgresql-devel python-lxml python-devel gcc patch python-setuptools
yum install -y gcc-c++ flex epel-release nginx supervisor

sudo amazon-linux-extras list | grep nginx

sudo amazon-linux-extras enable nginx1
        
sudo yum clean metadata
sudo yum -y install nginx
