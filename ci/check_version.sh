#!/bin/bash
set -ex

#############################################################################
#                                                                           #
# Copyright kubeinit contributors.                                          #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License"); you may   #
# not use this file except in compliance with the License. You may obtain   #
# a copy of the License at:                                                 #
#                                                                           #
# http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
# License for the specific language governing permissions and limitations   #
# under the License.                                                        #
#                                                                           #
#############################################################################

KUBEINIT_AGENT_VERSION=$(cat ./agent/setup.py | grep "_REVISION = '" | cut -d"'" -f2)
KUBEINIT_COLLECTION_VERSION=$(cat ./kubeinit/galaxy.yml | grep version | cut -d' ' -f2)
KUBEINIT_UI_VERSION=$(cat ./ui/package.json | jq .version | sed 's/"//g')
KUBEINIT_UI_PACKAGE_VERSION=$(cat ./ui/app/version.py | grep __version__ | cut -d'=' -f2 | sed 's/"//g' | sed 's/ //g')

echo "Agent version: $KUBEINIT_AGENT_VERSION"
echo "Collection version: $KUBEINIT_COLLECTION_VERSION"
echo "UI version: $KUBEINIT_UI_VERSION"
echo "UI package version: $KUBEINIT_UI_PACKAGE_VERSION"

if [ "${KUBEINIT_AGENT_VERSION}" == "${KUBEINIT_COLLECTION_VERSION}" ] && [ "${KUBEINIT_AGENT_VERSION}" == "${KUBEINIT_UI_VERSION}" ] && [ "${KUBEINIT_AGENT_VERSION}" == "${KUBEINIT_UI_PACKAGE_VERSION}" ]; then
    echo "Version match"
else
    echo "Version do not match"
    exit 1
fi
