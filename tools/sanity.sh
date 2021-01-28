#!/bin/bash

rm -rf kubeinit/releases
mkdir -p kubeinit/releases
cd kubeinit

# Build and install the collection
rm -rf ~/.ansible/collections/ansible_collections/kubeinit/kubeinit
ansible-galaxy collection build -v --force --output-path releases/
ansible-galaxy collection install --force --force-with-deps releases/kubeinit-kubeinit-`cat galaxy.yml | shyaml get-value version`.tar.gz
cd ~/.ansible/collections/ansible_collections/kubeinit/kubeinit

export HOME=$(eval echo ~$USER)

ansible-test sanity \
    --skip-test pylint \
    --skip-test future-import-boilerplate \
    --skip-test shebang \
    --skip-test metaclass-boilerplate \
    -v --docker --python 2.7
