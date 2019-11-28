# How to run this role

To deploy the demo server:

## Platform deployment

* Provision the environment packages using libvirt:

```bash
ansible-playbook \
    --user root \
    -vv -i ./hosts/demo-noha/inventory \
    -l hypervisor-nodes \
    --become \
    --become-user root \
    --tags provision_libvirt \
    ./playbook.yml
```

After provisioning the environment, this command should work.

This will prove connectivity between the provisioning node
and all the nodes to be configured in this guide.

**They all need to SUCCESS before continue**

```bash
ansible --user root -i ./hosts/demo-noha/inventory -m ping all
```

If there are nodes not responding is because the virsh interface attach
command didn't work as expected or is not refreshed correctly in the guests.
So we run a task to wake up those zombies.

We will run the wake up routine in both groups (masters and workers).

```bash
ansible-playbook \
    --user root \
    -vv -i ./hosts/demo-noha/inventory \
    -l kubernetes-master-nodes:kubernetes-worker-nodes  \
    --become \
    --become-user root \
    --tags provision_libvirt_restart_zombies \
    ./playbook.yml
```

## Kubernetes deployment

* Install the kubernetes cluster (master nodes):

```bash
ansible-playbook \
    --user root \
    -vv -i ./hosts/demo-noha/inventory \
    -l kubernetes-master-nodes \
    --become \
    --become-user root \
    --tags kubernetes_common,kubernetes_master \
    ./playbook.yml
```

```bash
ansible --user root -i ./hosts/demo-noha/inventory -m ping all
```

* Install the kubernetes cluster (worker nodes):

```bash
ansible-playbook \
    --user root \
    -vv -i ./hosts/demo-noha/inventory \
    -l kubernetes-worker-nodes \
    --become \
    --become-user root \
    --tags kubernetes_common,kubernetes_worker \
    ./playbook.yml
```

```bash
ansible --user root -i ./hosts/demo-noha/inventory -m ping all
```

* Install kubernetes base apps (master nodes):

```bash
ansible-playbook \
    --user root \
    -vv -i ./hosts/demo-noha/inventory \
    -l kubernetes-master-nodes \
    --become \
    --become-user root \
    --tags kubernetes_deploy_apps \
    ./playbook.yml
```

## Pystol deployment

* Install Pystol:

```bash
ansible-playbook \
    --user root \
    -vv -i ./hosts/demo-noha/inventory \
    -l kubernetes-master-nodes \
    --become \
    --become-user root \
    --tags pystol_install \
    ./playbook.yml
```
