#!/bin/bash
set -e

# This job will:
# Deploy two kubernetes clusters,
# it will install subctl in the services nodes of the broker cluster,
# it will create a submariner broker cluster,
# it will install subctl in the services nodes of the seconday node,
# and it will join the secondary cluster to the broker.

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
    ./playbooks/submariner.yml

# Deploy submariner as secondary (rke)
ansible-playbook \
    --user root \
    -v -i ./hosts/rke/inventory \
    --become \
    --become-user root \
    -e kubeinit_submariner_is_secondary=True \
    ./playbooks/submariner.yml
