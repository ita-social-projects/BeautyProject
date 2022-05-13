#!/bin/bash

isExistApp = `sudo pgrep nginx`
if [[ -n  $isExistApp ]]; then
    sudo nginx -s stop        
fi
