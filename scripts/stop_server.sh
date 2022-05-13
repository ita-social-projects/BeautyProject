#!/bin/bash

isExistApp = `pgrep nginx`
if [[ -n  $isExistApp ]]; then
    sudo nginx -s stop        
fi
