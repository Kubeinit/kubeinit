## How to run this role

To deploy the demo server:

* Provision the environment packages using libvirt:

```bash
ansible-playbook \
    --user root \
    -v -i ./hosts/demo/inventory \
    -l hypervisor-nodes \
    --extra="ansible_ssh_common_args='-o StrictHostKeyChecking=no'" \
    --become \
    --become-user root \
    --tags provision_libvirt \
    ./playbook.yml
```

* Install the kubernetes cluster (master nodes):

```bash
ansible-playbook \
    --user root \
    -v -i ./hosts/demo/inventory \
    -l kubernetes-master-nodes \
    --extra="ansible_ssh_common_args='-o StrictHostKeyChecking=no'" \
    --become \
    --become-user root \
    --tags common,master \
    ./playbook.yml
```

* Install the kubernetes cluster (worker nodes):

```bash
ansible-playbook \
    --user root \
    -v -i ./hosts/demo/inventory \
    -l kubernetes-worker-nodes \
    --extra="ansible_ssh_common_args='-o StrictHostKeyChecking=no'" \
    --become \
    --become-user root \
    --tags common,worker \
    ./playbook.yml
```

* Install Pystol:

```bash
ansible-playbook \
    --user root \
    -v -i ./hosts/demo/inventory \
    -l kubernetes-master-nodes \
    --extra="ansible_ssh_common_args='-o StrictHostKeyChecking=no'" \
    --become \
    --become-user root \
    --tags pystol_install \
    ./playbook.yml
```
