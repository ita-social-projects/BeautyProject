#!/bin/bash

if [ -e /var/run/nginx.pid ]; then sudo nginx -s stop; fi
