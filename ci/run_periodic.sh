#!/bin/bash
set -e

echo "Executing run.sh"

BRANCH_NAME="$1"
PULL_REQUEST="$2"
VARS_YAML_PATH="$3"
DISTRO="$4"
DRIVER="$5"
MASTER="$6"
WORKER="$7"
SCENARIO="$8"

echo "The branch is $BRANCH_NAME"
echo "The pull request is $PULL_REQUEST"
echo "The vars.yaml path is: $VARS_YAML_PATH"
echo "The distro is $DISTRO"
echo "The driver is $DRIVER"
echo "The amount of master nodes is $MASTER"
echo "The amount of worker nodes is $WORKER"
echo "The scenario is $SCENARIO"

# Install and configure ara
# There are problems with multithread ara, we keep the last
# single thread version
python3 -m pip install --upgrade "ara[server]"==1.5.6

# This will nuke the ara database so in each run we have a clean env
rm /root/.ara/server/ansible.sqlite
ara-manage migrate

rm -rf ~/badge_status.svg

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

# Here we might define some different
# variables depending on the scenario
if [[ "$DISTRO" == "okd.rke" && "$DRIVER" == "libvirt" ]]; then
sudo tee scenario_variables.yml > /dev/null <<EOF
kubeinit_common_dns_public: 10.64.63.6
kubeinit_libvirt_destroy_all_guests: False
EOF
else
sudo tee scenario_variables.yml > /dev/null <<EOF
kubeinit_common_dns_public: 10.64.63.6
kubeinit_libvirt_destroy_all_guests: True
EOF
fi

echo "The content of the scenario_variables.yml file is:"

cat scenario_variables.yml

# We need to remove any created VM in other jobs
# TODO: Add cleanup tasks

for i in $(virsh -q list | awk '{ print $2 }'); do
    virsh destroy $i;
    virsh undefine $i --remove-all-storage;
done;
for i in $(virsh -q net-list | awk '{ print $1 }'); do
    virsh net-destroy $i;
    virsh net-undefine $i;
done;

# By default we deploy 3 master and 1 worker cluster
# the case of 3 master is already by default
# the case of 1 worker is already by default
# We use the .*- expresion to comment the line
# no matter the distro, i.e., okd-master or k8s-master
if [[ "$DISTRO" == "okd.rke" ]]; then
    if [[ "$MASTER" == "1" ]]; then
        sed -i -E "s/.*-controller-02/#-controller-02/g" ./hosts/okd/inventory
        sed -i -E "s/.*-controller-02/#-controller-02/g" ./hosts/rke/inventory
        sed -i -E "s/.*-controller-02/#-controller-02/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-controller-02/#-controller-02/g" ./hosts/cdk/inventory
        sed -i -E "s/.*-controller-02/#-controller-02/g" ./hosts/eks/inventory

        sed -i -E "s/.*-controller-03/#-controller-03/g" ./hosts/okd/inventory
        sed -i -E "s/.*-controller-03/#-controller-03/g" ./hosts/rke/inventory
        sed -i -E "s/.*-controller-03/#-controller-03/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-controller-03/#-controller-03/g" ./hosts/cdk/inventory
        sed -i -E "s/.*-controller-03/#-controller-02/g" ./hosts/eks/inventory
    fi

    if [[ "$WORKER" == "0" ]]; then
        sed -i -E "s/.*-compute-01/#-compute-01/g" ./hosts/okd/inventory
        sed -i -E "s/.*-compute-01/#-compute-01/g" ./hosts/rke/inventory
        sed -i -E "s/.*-compute-01/#-compute-01/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-compute-01/#-compute-01/g" ./hosts/cdk/inventory
        sed -i -E "s/.*-compute-01/#-compute-01/g" ./hosts/eks/inventory

        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/okd/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/rke/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/cdk/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/eks/inventory
    fi

    if [[ "$WORKER" == "1" ]]; then
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/okd/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/rke/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/cdk/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/eks/inventory
    fi

    sed -i "s/10.0.0.1 /10.0.0.201 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.2 /10.0.0.202 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.3 /10.0.0.203 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.4 /10.0.0.204 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.5 /10.0.0.205 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.6 /10.0.0.206 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.7 /10.0.0.207 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.8 /10.0.0.208 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.9 /10.0.0.209 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.10 /10.0.0.210 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.11 /10.0.0.211 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.12 /10.0.0.212 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.13 /10.0.0.213 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.14 /10.0.0.214 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.15 /10.0.0.215 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.100 /10.0.0.250 /g" ./hosts/rke/inventory
    sed -i "s/10.0.0.100/10.0.0.250/g" ./hosts/rke/inventory

    # Deploy the fisrt cluster (okd)
    ansible-playbook \
        --user root \
        -v -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        -e kubeinit_bind_multicluster_dns_forward_enabled=True \
        -e @scenario_variables.yml \
        ./playbooks/okd.yml

    # Deploy the second cluster (rke)
    ansible-playbook \
        --user root \
        -v -i ./hosts/rke/inventory \
        --become \
        --become-user root \
        -e kubeinit_bind_multicluster_dns_forward_enabled=True \
        -e kubeinit_libvirt_multicluster_keep_predefined_networks=True \
        -e @scenario_variables.yml \
        ./playbooks/rke.yml

    # Deploy submariner as broker (rke)
    ansible-playbook \
        --user root \
        -v -i ./hosts/rke/inventory \
        --become \
        --become-user root \
        -e kubeinit_submariner_is_broker=True \
        -e @scenario_variables.yml \
        ./playbooks/submariner.yml

    # Deploy submariner as secondary (okd)
    ansible-playbook \
        --user root \
        -v -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        -e kubeinit_submariner_is_secondary=True \
        -e @scenario_variables.yml \
        ./playbooks/submariner.yml

    # Run subctl verify to check cluster status in the sec cluster (okd)
    ansible-playbook \
        --user root \
        -v -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        -e kubeinit_submariner_is_secondary=True \
        -e @scenario_variables.yml \
        ./playbooks/submariner-subctl-verify.yml

elif [[ "$DISTRO" == "k8s.ovn" ]]; then
    if [[ "$MASTER" == "1" ]]; then
        sed -i -E "s/.*-controller-02/#-controller-02/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-controller-03/#-controller-03/g" ./hosts/k8s/inventory
    fi

    if [[ "$WORKER" == "0" ]]; then
        sed -i -E "s/.*-compute-01/#-compute-01/g" ./hosts/k8s/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/k8s/inventory
    fi

    if [[ "$WORKER" == "1" ]]; then
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/k8s/inventory
    fi

    # We rename nyctea to nycteaa
    sed -i -E "s/ansible_host=nyctea/ansible_host=nycteaa/g" ./hosts/k8s/inventory
    # We enable other 2 HVs
    sed -i -E "/# hypervisor-02 ansible_host=tyto/ s/# //g" ./hosts/k8s/inventory
    sed -i -E "/# hypervisor-03 ansible_host=strix/ s/# //g" ./hosts/k8s/inventory

    # We balance the cluster nodes across the HVs
    sed -i -E "/k8s-controller-01 ansible_host/ s/hypervisor-01/hypervisor-01/g" ./hosts/k8s/inventory
    sed -i -E "/k8s-controller-02 ansible_host/ s/hypervisor-01/hypervisor-01/g" ./hosts/k8s/inventory
    sed -i -E "/k8s-controller-03 ansible_host/ s/hypervisor-01/hypervisor-02/g" ./hosts/k8s/inventory

    sed -i -E "/k8s-compute-01 ansible_host/ s/hypervisor-01/hypervisor-02/g" ./hosts/k8s/inventory
    sed -i -E "/k8s-compute-02 ansible_host/ s/hypervisor-01/hypervisor-03/g" ./hosts/k8s/inventory

    sed -i -E "/k8s-service-01 ansible_host/ s/hypervisor-01/hypervisor-03/g" ./hosts/k8s/inventory

    ansible-playbook \
        --user root \
        -v -i ./hosts/k8s/inventory \
        --become \
        --become-user root \
        -e @scenario_variables.yml \
        ./playbooks/k8s.yml
else
    if [[ "$MASTER" == "1" ]]; then
        sed -i -E "s/.*-controller-02/#-controller-02/g" ./hosts/$DISTRO/inventory
        sed -i -E "s/.*-controller-03/#-controller-03/g" ./hosts/$DISTRO/inventory
    fi

    if [[ "$WORKER" == "0" ]]; then
        sed -i -E "s/.*-compute-01/#-compute-01/g" ./hosts/$DISTRO/inventory
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/$DISTRO/inventory
    fi

    if [[ "$WORKER" == "1" ]]; then
        sed -i -E "s/.*-compute-02/#-compute-02/g" ./hosts/$DISTRO/inventory
    fi

    ansible-playbook \
        --user root \
        -v -i ./hosts/$DISTRO/inventory \
        --become \
        --become-user root \
        -e @scenario_variables.yml \
        ./playbooks/$DISTRO.yml
fi
