#!/bin/bash
set -e

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

count=`find . -not -wholename "*/node_modules/*" -and -not -wholename "*.tox/*" -and -name "*.yaml" | wc -l`
if [ "$count" != "0" ]; then
    echo "yaml extension not allowed"
    exit 1
else
    echo "no yaml found"
fi


# Match both docs and modules/roles

roles_docs_number=`ls docs/src/roles | grep -v pycache | wc -l`
roles_readmes_number=`find kubeinit/roles/ -name README.md | grep -v pycache | wc -l`
roles_number=`ls kubeinit/roles/ | grep -v pycache | wc -l`

modules_docs_number=`ls docs/src/modules | grep -v pycache | wc -l`
modules_number=`ls kubeinit/plugins/modules/ | grep -v pycache | wc -l`

echo "Roles in docs: $roles_docs_number"
echo "Roles: $roles_number"
echo "Roles READMEs: $roles_readmes_number"

echo "Modules in docs: $modules_docs_number"
echo "Modules: $modules_number"

if [ "$roles_readmes_number" -ne "$roles_number" ];then
    echo "The README.md file in each role do not";
    echo "match with the number of existing roles";
    exit 1;
fi

if [ "$roles_docs_number" -ne "$roles_number" ];then
    echo "Links in the roles docs section";
    echo "do not match with the number of existing roles";
    exit 1;
fi

if [ "$modules_docs_number" -ne "$modules_number" ];then
    echo "Links in the modules docs section";
    echo "do not match with the number of existing modules";
    exit 1;
fi
