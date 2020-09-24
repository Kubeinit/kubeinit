<p style="text-align: center" align="center">
    <a href="https://www.kubeinit.com"><img src="https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo.svg?sanitize=true" alt="The KUBErnetes INITiator"/></a>
</p>

**The KUBErnetes INITiator**

<p style="text-align: center" align="center">
    <a href="https://www.python.org"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-python.svg?sanitize=true"/> </a>
    <a href="https://www.ansible.com"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-ansible.svg?sanitize=true"/> </a>
    <a href="https://www.kubeinit.com"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-love.svg?sanitize=true"/> </a>
    <a href="https://www.kubeinit.com"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/cloud-native.svg?sanitize=true"/> </a>
</p>

<p style="text-align: center" align="center">
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=linters"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/linters/badge.svg?event=push"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=units"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/units/badge.svg?event=push"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=docs_build"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/docs_build/badge.svg?event=push"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=molecule"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/molecule/badge.svg?event=push"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=galaxy_publish"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/galaxy_publish/badge.svg?event=push"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=container_image"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/container_image/badge.svg?event=push"/> </a>
    <a href="https://opensource.org/licenses/Apache-2.0"><img height="20px" src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"/> </a>
</p>

# What is KubeInit?

KubeInit provides Ansible playbooks and roles for the deployment and configuration of multiple Kubernetes distributions.

# Mission

KubeInit's mission is to have a fully automated way to deploy in a single command a curated list of
prescribed architectures based on the following principles **(G.I.V.E.)**.

**G**uide new and experienced users and contributors to deploy quickly and easily
Kubernetes clusters based on a set of prescribed architectures.

**I**ncentivate new users and contributors to overcoming the learning curve to
successfully deploy complex Kubernetes scenarios.

**V**erify automatically that the defined prescribed architectures work seamlessly.

**E**ngage with the upstream community for giving and receiving feedback,
and cross-pollination to spark and amplify creativity, serendipity, and interdisciplinary friction.

# Documentation

KubeInit's documentation is hosted in [this same repository](https://docs.kubeinit.com).

# KubeInit supported scenarios

**K8s distribution:** OKD

**Driver:** Libvirt

**OS:** CentOS/Fedora, Debian/Ubuntu	

# Requirements

* A fresh deployed server with enough RAM and disk space (120GB in RAM and 300GB in disk) and CentOS 8 (it should work also in Fedora/Debian/Ubuntu hosts).
* We assume that the hypervisor node is called nyctea (defined in the inventory).
* Have root passwordless access with certificates.
* Adjust the inventory file to suit your needs i.e. [the worker nodes](https://github.com/Kubeinit/kubeinit/blob/master/kubeinit/hosts/okd/inventory#L66)
 you will need in your cluster.

# How to run

There are two ways of launching Kubeinit, directly using the
ansible-playbook command, or by running it inside a container.

## Directly executing the deployment playbook

The following example command will deploy a multi-master OKD 4.5 cluster with 1 worker node
in a single command and in approximately 30 minutes.

```bash
git clone https://github.com/Kubeinit/kubeinit.git
cd kubeinit
ansible-playbook \
    --user root \
    -v -i ./hosts/okd/inventory \
    --become \
    --become-user root \
    ./playbooks/okd.yml
```

After provisioning any of the scenarios, you should have your environment ready to go.
To connect to the nodes from the hypervisor use the IP addresses from the inventory files.

## Running the deployment command from a container

The whole process is explained in the [HowTo's](https://www.anstack.com/blog/2020/09/11/Deploying-KubeInit-from-a-container.html).
The following commands build a container image with the project inside of it, and then
launches the container executing the ansible-playbook command with all the
standard ansible-playbook parameters.

```
git clone https://github.com/Kubeinit/kubeinit.git
cd kubeinit
podman build -t kubeinit/kubeinit .

podman run --rm -it \
    -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:z \
    -v /etc/hosts:/etc/hosts \
    kubeinit/kubeinit \
        --user root \
        -v -i ./hosts/okd/inventory \
        --become \
        --become-user root \
        ./playbooks/okd.yml
```

# HowTo's and presentations

* [The easiest and fastest way to deploy an OKD 4.5 cluster in a Libvirt/KVM Host](https://www.anstack.com/blog/2020/07/31/the-fastest-and-simplest-way-to-deploy-okd-openshift-4-5.html).
* [KubeInit external access for OpenShift/OKD deployments with Libvirt](https://www.anstack.com/blog/2020/08/25/KubeInit-External-access-for-OpenShift-OKD-deployments-with-Libvirt.html).
* [Deploying KubeInit from a container](https://www.anstack.com/blog/2020/09/11/Deploying-KubeInit-from-a-container.html).
* [KubeInit: Bringing good practices from the OpenStack ecosystem to improve the way OKD/OpenShift deploys](https://www.twitch.tv/videos/750577055), [slides](https://speakerdeck.com/redhatopenshift/openshift-deploys).