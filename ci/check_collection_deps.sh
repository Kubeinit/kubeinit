#!/bin/bash
set -o pipefail
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

read-0() {
    while [ "$1" ]; do
        IFS=$'\0' read -r -d '' "$1" || return 1
        shift
    done
} &&
cat kubeinit/galaxy.yml | shyaml key-values-0 dependencies |
while read-0 key value; do
    fval=$(echo "${value}" | tr -d '=')
    sval=$(cat kubeinit/requirements.yml | shyaml get-value collections | grep -A1 ${key} | grep -v ${key} | cut -d ':' -f 2 | tr -d ' ')
    if [ "$fval" = "$sval" ]; then
        echo "Versions for ${key} are the same in requirements.yml and galaxy.yml"
    else
        echo "For the ${key} dependency there is a mismatch in"
        echo "/kubeinit/kubeinit/requirements.yml and /kubeinit/kubeinit/galaxy.yml"
        echo "Both versions should be the same"
        exit 1
    fi
done
