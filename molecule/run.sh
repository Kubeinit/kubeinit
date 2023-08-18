#!/usr/bin/env bash
# Copyright 2019 Red Hat, Inc.
# Copyright 2020 KubeInit

# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

set -o pipefail
set -xeuo

if [ ! -f tox.ini ]; then
    echo "EXECUTE THIS SCRIPT FROM THE REPOSITORY ROOT DIRECTORY"
    echo "EXECUTE THIS SCRIPT FROM THE REPOSITORY ROOT DIRECTORY"
    echo "EXECUTE THIS SCRIPT FROM THE REPOSITORY ROOT DIRECTORY"
    echo "EXECUTE THIS SCRIPT FROM THE REPOSITORY ROOT DIRECTORY"
    echo "like: ./molecule/run.sh"
    exit 1
fi

# Install Molecule Python requirements
python3 -m pip install -r ./molecule/molecule-requirements.txt

# Install Kubeinit and Molecule Ansible collections requirements
ansible-galaxy collection install --force -r ./kubeinit/requirements.yml
ansible-galaxy collection install --force -r ./molecule/molecule-requirements.yml

# Run molecule
cd ./kubeinit/roles/
python3 -m pytest \
        --trace \
        --color=no \
        --html=/tmp/reports.html \
        --self-contained-html
