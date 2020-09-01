#!/bin/bash

rm -rf kubeinit/releases
mkdir -p kubeinit/releases
cd kubeinit

# Build and install the collection
rm -rf ~/.ansible/collections/ansible_collections/kubeinit/kubeinit
ansible-galaxy collection build -v --force --output-path releases/
ansible-galaxy collection install --force releases/kubeinit-kubeinit-`cat galaxy.yml | shyaml get-value version`.tar.gz
cd ~/.ansible/collections/ansible_collections/kubeinit/kubeinit

# In the GitHub actions this variable is not defined.
if [[ -z "${HOME}" ]]; then
    export HOME=/home/runner
fi

ansible-test sanity --skip-test import
