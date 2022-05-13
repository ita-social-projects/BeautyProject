#!/bin/bash

isExistApp = `pgrep -n nginx`
if [ $isExistApp ]; then
    sudo nginx -s stop        
fi
