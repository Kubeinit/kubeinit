#!/bin/bash

count=`find . -not -wholename "*/node_modules/*" -and -not -wholename "*.tox/*" -and -name "*.yaml" | wc -l`
if [ "$count" != "0" ]; then
    echo "yaml extension not allowed"
    # exit 1
else
    echo "no yaml found"
fi
