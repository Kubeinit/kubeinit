#!/bin/bash
set -e

BRANCH_NAME="$1"
PULL_REQUEST="$2"
VARS_YAML_PATH="$3"
DISTRO="$4"
DRIVER="$5"

echo "The branch is $BRANCH_NAME"
echo "The pull request is $PULL_REQUEST"
echo "The vars.yaml path is: $VARS_YAML_PATH"
echo "The distro is $DISTRO"
echo "The driver is $DRIVER"

# Clone the repo
rm -rf tmp
mkdir -p tmp
cd tmp
git clone -n https://github.com/kubeinit/kubeinit.git -b $BRANCH_NAME
cd kubeinit
git fetch origin pull/$PULL_REQUEST/head
git checkout -b pr  FETCH_HEAD
git log -n 5 --pretty=oneline

# TODO:Remove when merged
# Keep as an example for cherry-picking workarounds
# git remote add ccamacho https://github.com/ccamacho/kubeinit.git
# git fetch ccamacho
# git cherry-pick 58f718a29d5611234304b1e144a69

if [[ "$DISTRO" == "okd" && "$DRIVER" == "libvirt" ]]; then
cat << EOF > scenario_variables.yml
kubeinit_libvirt_test_variable: asdf
kubeinit_libvirt_test_variable1: asdf
EOF
fi

#
# We need to receive here some parameters, the source and destination
# tenants should be defined depending on where we will need to run the job
#

ansible-playbook \
    --user root \
    -v -i ./hosts/okd/inventory \
    --become \
    --become-user root \
    -e @scenario_variables.yml \
    ./playbooks/$DISTRO.yml
