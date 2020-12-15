#!/bin/bash

KUBEINIT_AGENT_VERSION=$(cat ./agent/setup.py | grep "_REVISION = '" | cut -d"'" -f2)
KUBEINIT_COLLECTION_VERSION=$(cat ./kubeinit/galaxy.yml | grep version | cut -d' ' -f2)
#KUBEINIT_UI_VERSION=$(cat ./ui/package.json | grep version | cut -d'"' -f4)

if [[ "$KUBEINIT_AGENT_VERSION" == "$KUBEINIT_COLLECTION_VERSION" ]]; then
    echo "Version match"
else
    echo "Version do not match"
    exit 1
fi
