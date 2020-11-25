#!/bin/bash

echo "Executing run_submariner.sh"

BRANCH_NAME="$1"
PULL_REQUEST="$2"
VARS_YAML_PATH="$3"
DISTRO="$4"
DRIVER="$5"
MASTER="$6"
WORKER="$7"
SCENARIO="$8"
PIPELINE_ID="$9"

echo "The branch is $BRANCH_NAME"
echo "The pull request is $PULL_REQUEST"
echo "The vars.yaml path is: $VARS_YAML_PATH"
echo "The distro is $DISTRO"
echo "The driver is $DRIVER"
echo "The amount of master nodes is $MASTER"
echo "The amount of worker nodes is $WORKER"
echo "The scenario is $SCENARIO"

# Install and configure ara
python3 -m pip install "ara[server]"

# This will nuke the ara database so in each run we have a clean env
rm /root/.ara/server/ansible.sqlite


export ANSIBLE_CALLBACK_PLUGINS="$(python3 -m ara.setup.callback_plugins)"

# Clone the repo
rm -rf tmp
mkdir -p tmp
cd tmp
git clone https://github.com/kubeinit/kubeinit.git
cd kubeinit

# TODO:Remove when merged
# Keep as an example for cherry-picking workarounds
# git remote add ccamacho https://github.com/ccamacho/kubeinit.git
# git fetch ccamacho
# git cherry-pick 58f718a29d5611234304b1e144a69

sudo tee scenario_variables.yml > /dev/null <<EOF
kubeinit_submariner_test_pr_url: "https://github.com/submariner-io/submariner-operator/pull/$PULL_REQUEST"
EOF

echo "The content of the scenario_variables.yml file is:"

cat scenario_variables.yml

# By default we deploy 3 master and 1 worker cluster
# the case of 3 master is already by default
# the case of 1 worker is already by default
# We use the .*- expresion to comment the line
# no matter the distro, i.e., okd-master or k8s-master
if [[ "$DISTRO" == "multiple" ]]; then
    if [[ "$MASTER" == "1" ]]; then
        sed -i -E "s/.*-master-02/#-master-02/g" ./hosts/okd/inventory
        sed -i -E "s/.*-master-02/#-master-02/g" ./hosts/rke/inventory
        sed -i -E "s/.*-master-02/#-master-02/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-master-02/#-master-02/g" ./hosts/cdk/inventory

        sed -i -E "s/.*-master-03/#-master-03/g" ./hosts/okd/inventory
        sed -i -E "s/.*-master-03/#-master-03/g" ./hosts/rke/inventory
        sed -i -E "s/.*-master-03/#-master-03/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-master-03/#-master-03/g" ./hosts/cdk/inventory
    fi

    if [[ "$WORKER" == "0" ]]; then
        sed -i -E "s/.*-worker-01/#-worker-01/g" ./hosts/okd/inventory
        sed -i -E "s/.*-worker-01/#-worker-01/g" ./hosts/rke/inventory
        sed -i -E "s/.*-worker-01/#-worker-01/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-worker-01/#-worker-01/g" ./hosts/cdk/inventory
    fi

    if [[ "$WORKER" == "2" ]]; then
        sed -i -E "/# .*-worker-02/ s/# //g" ./hosts/okd/inventory
        sed -i -E "/# .*-worker-02/ s/# //g" ./hosts/rke/inventory
        sed -i -E "/# .*-worker-02/ s/# //g" ./hosts/k8s/inventory
        sed -i -E "/# .*-worker-02/ s/# //g" ./hosts/cdk/inventory
    fi
else
    if [[ "$MASTER" == "1" ]]; then
        sed -i -E "s/.*-master-02/#-master-02/g" ./hosts/$DISTRO/inventory
        sed -i -E "s/.*-master-03/#-master-03/g" ./hosts/$DISTRO/inventory
    fi

    if [[ "$WORKER" == "0" ]]; then
        sed -i -E "s/.*-worker-01/#-worker-01/g" ./hosts/$DISTRO/inventory
    fi

    if [[ "$WORKER" == "2" ]]; then
        sed -i -E "/# .*-worker-02/ s/# //g" ./hosts/$DISTRO/inventory
    fi
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

if [[ "$SCENARIO" == "submariner" ]]; then

    # This will:
    # Deploy two kubernetes clusters,
    # it will install subctl in the services nodes of the broker cluster,
    # it will create a submariner broker cluster,
    # it will install subctl in the services nodes of the seconday node,
    # and it will join the secondary cluster to the broker.
    # Also it will pass an extra variable with the patch to test

    # Deploy the fisrt cluster (okd)
    ansible-playbook \
        --user root \
        -v -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        -e kubeinit_libvirt_dns_forward_multicluster_enabled=True \
        ./playbooks/okd.yml

    # Deploy the second cluster (rke)
    ansible-playbook \
        --user root \
        -v -i ./hosts/rke/inventory \
        --become \
        --become-user root \
        -e kubeinit_libvirt_dns_forward_multicluster_enabled=True \
        ./playbooks/rke.yml

    # Deploy submariner as broker (okd)
    ansible-playbook \
        --user root \
        -v -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        -e kubeinit_submariner_is_broker=True \
        -e @scenario_variables.yml \
        ./playbooks/submariner.yml

    # Deploy submariner as secondary (rke)
    ansible-playbook \
        --user root \
        -v -i ./hosts/rke/inventory \
        --become \
        --become-user root \
        -e kubeinit_submariner_is_secondary=True \
        -e @scenario_variables.yml \
        ./playbooks/submariner.yml
fi

echo "Running ara-manage to store the results"
ara-manage generate ./$PIPELINE_ID
ls -ltah
pwd
chmod -R 755 ./$PIPELINE_ID

curl -OL https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo_white.svg
curl -OL https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/icon.png
mv logo.svg ./$PIPELINE_ID/static/images/logo.svg
mv icon.png ./$PIPELINE_ID/static/images/favicon.ico

find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's/ARA Records Ansible/KubeInit job report/g' {} \;
find ./$PIPELINE_ID -type f -name '*.html' -exec sed -i -e 's/ara.readthedocs.io/docs.kubeinit.com/g' {} \;

echo "Finishing the bash executor"
