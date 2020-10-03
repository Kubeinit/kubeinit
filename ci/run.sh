#!/bin/bash
set -e

BRANCH_NAME="$1"
PULL_REQUEST="$2"
VARS_YAML_PATH="$3"
DISTRO="$4"
DRIVER="$5"
MASTER="$6"
WORKER="$7"

echo "The branch is $BRANCH_NAME"
echo "The pull request is $PULL_REQUEST"
echo "The vars.yaml path is: $VARS_YAML_PATH"
echo "The distro is $DISTRO"
echo "The driver is $DRIVER"
echo "The amount of master nodes is $MASTER"
echo "The amount of worker nodes is $WORKER"

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

# By default we deploy 3 master and 1 worker cluster
# the case of 3 master is already by default
# the case of 1 worker is already by default

if [[ "$MASTER" == "1" ]]; then
sed -i "s/okd-master-02/#okd-master-02/g" ./hosts/okd/inventory
sed -i "s/okd-master-03/#okd-master-03/g" ./hosts/okd/inventory
fi

if [[ "$WORKER" == "0" ]]; then
sed -i "s/okd-worker-01/#okd-worker-01/g" ./hosts/okd/inventory
fi

# We need to remove any created VM in other jobs
# TODO: Add cleanup tasks

for i in $(virsh -q list | awk '{ print $2 }'); do
    virsh destroy $i;
    virsh undefine $i --remove-all-storage;
done;

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
