#!/bin/bash

sudo yum update -y

sudo yum install gcc libc-dev linux-headers postgresql-dev postgresql-client

sudo amazon-linux-extras list | grep nginx

sudo amazon-linux-extras enable nginx1
        
sudo yum clean metadata
sudo yum -y install nginx
