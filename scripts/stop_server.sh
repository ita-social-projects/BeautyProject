#!/bin/bash

isExistApp = `pgrep nginx`
if [[ $isExistApp ]]; then
    sudo nginx -s stop     
fi
