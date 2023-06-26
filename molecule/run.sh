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

## Shell Opts ----------------------------------------------------------------

set -o pipefail
set -xeuo

## Vars ----------------------------------------------------------------------
export PROJECT_DIR=${PWD}
export ANSIBLE_REMOTE_TMP=/tmp/$USER/ansible

if [ ! -f tox.ini ]; then
    echo "EXECUTE THIS SCRIPT FROM THE REPOSITORY ROOT DIRECTORY"
    echo "EXECUTE THIS SCRIPT FROM THE REPOSITORY ROOT DIRECTORY"
    echo "EXECUTE THIS SCRIPT FROM THE REPOSITORY ROOT DIRECTORY"
    echo "EXECUTE THIS SCRIPT FROM THE REPOSITORY ROOT DIRECTORY"
    echo "like: ./molecule/run.sh"
    exit 1
fi

## Install the collection --------------
# VERSION=$(grep '^version: ' kubeinit/galaxy.yml | awk '{print $2}')
# ansible-galaxy collection build kubeinit -v --force --output-path releases/
# cd releases/
# ln -sf kubeinit-kubeinit-$VERSION.tar.gz kubeinit-kubeinit-latest.tar.gz
# ansible-galaxy collection install --force kubeinit-kubeinit-latest.tar.gz
# cd ..

## Main ----------------------------------------------------------------------

# Create a virtual env
python3 -m virtualenv --system-site-packages "${HOME}/test-python"

# Install local requirements
if [[ -d "${HOME}/.cache/pip/wheels" ]]; then
    rm -rf "${HOME}/.cache/pip/wheels"
fi

"${HOME}/test-python/bin/pip" install \
    -r "${PROJECT_DIR}/molecule/molecule-requirements.txt"

# Run local test
PS1="[\u@\h \W]\$" source "${HOME}/test-python/bin/activate"

cd ./kubeinit/roles/
python3 -m pytest \
        --trace \
        --color=no \
        --html=/tmp/reports.html \
        --self-contained-html
