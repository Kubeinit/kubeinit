<p style="text-align: center" align="center">
    <a href="https://www.kubeinit.org"><img src="https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo.svg?sanitize=true" alt="The KUBErnetes INITiator"/></a>
</p>

**The KUBErnetes INITiator**

<p style="text-align: center" align="center">
    <a href="https://www.python.org"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-python.svg?sanitize=true"/> </a>
    <a href="https://www.ansible.com"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-ansible.svg?sanitize=true"/> </a>
    <a href="https://www.kubeinit.org"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-love.svg?sanitize=true"/> </a>
    <a href="https://www.kubeinit.org"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/cloud-native.svg?sanitize=true"/> </a>
</p>

<p style="text-align: center" align="center">
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=docs_build"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/docs_build/badge.svg?event=schedule"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=linters"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/linters/badge.svg?event=schedule"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=units"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/units/badge.svg?event=schedule"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=molecule"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/molecule/badge.svg?event=schedule"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=release"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/release/badge.svg?event=push"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=container_image"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/container_image/badge.svg?event=schedule"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=distro_test"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/distro_test/badge.svg?event=schedule"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=check_package_build"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/check_package_build/badge.svg?event=schedule"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=quay_mirror"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/quay_mirror/badge.svg?event=schedule"/> </a>
    <a href="https://kubernetes.slack.com/archives/C01FKK19T0B"><img height="20px" src="https://img.shields.io/badge/chat-on%20slack-blue.svg?logo=slack&longCache=true&style=flat"/> </a>
</p>

# What is KubeInit?

KubeInit provides Ansible playbooks and roles for the deployment
and configuration of multiple Kubernetes distributions.
KubeInit's mission is to have a fully automated way to deploy in
a single command a curated list of prescribed architectures.

## Documentation

KubeInit's documentation is hosted in [this same repository](https://docs.kubeinit.org).

## Periodic jobs status

There is a set of predefined scenarios that are tested on
a weekly basis, the result of those executions is
presented in the [periodic job execution page](periodic_jobs.md).


## KubeInit supported scenarios

**K8s distribution:** OKD (testing K8S, RKE, EKS, RKE)

**Driver:** Libvirt

**OS:** CentOS/Fedora, Debian/Ubuntu

## Requirements

* A fresh deployed server with enough RAM and disk space (120GB in RAM and 300GB in disk) and CentOS 8 (it should work also in Fedora/Debian/Ubuntu hosts).
* Adjust the inventory file to suit your needs.
* By default the first hypervisor node is called nyctea (defined in the inventory). Replace it with the hostname you specified if you changed it.
  You can also use the names in the inventory as aliases for your own hostnames using ~/.ssh/config (described in more detail below).
* Have root passwordless access with certificates.
* Having podman installed in the machine where you are running ansible-playbook.

### Check if nyctea is reachable via passwordless root access

If you need to setup aliases in ssh for nyctea, tyto, strix, or any other hypervisor hosts that
you have added or are mentioned in the inventory, you can create a file named config in ~/.ssh
with contents like this:

```bash
echo "Host nyctea" >> ~/.ssh/config
echo "  Hostname actual_hostname" >> ~/.ssh/config
```

For example, if you have a deployed server that you can already ssh into as root called `server.mysite.local`
you can create a ~/.ssh/config with these contents:

```
Host nyctea
  Hostname server.mysite.local
```

Now you should be ready to try access to your ansible host like this:

```bash
ssh root@nyctea
```

If it fails. check if you have an ssh key, and generate one if you don't

```bash
if [ -f ~/.ssh/id_rsa ]; then
  ssh-keygen
  ssh-copy-id /root/.ssh/id_rsa root@nyctea
fi
```

# How to run

There are two ways of launching Kubeinit, directly using the
ansible-playbook command, or by running it inside a container.

## Directly executing the deployment playbook

The following example command will deploy an OKD 4.8 cluster with a 3 node control-plane
and 1 worker node in a single command and in approximately 30 minutes.

```bash
# Install the requirements assuming python3/pip3 is installed
pip3 install \
        --upgrade \
        pip \
        shyaml \
        ansible \
        netaddr

# Get the project's source code
git clone https://github.com/Kubeinit/kubeinit.git
cd kubeinit

# Install the Ansible collection requirements
ansible-galaxy collection install --force --requirements-file kubeinit/requirements.yml

# Build and install the collection
rm -rf ~/.ansible/collections/ansible_collections/kubeinit/kubeinit
ansible-galaxy collection build kubeinit --verbose --force --output-path releases/
ansible-galaxy collection install --force --force-with-deps releases/kubeinit-kubeinit-`cat kubeinit/galaxy.yml | shyaml get-value version`.tar.gz

# Run the playbook
ansible-playbook \
    -v --user root \
    -e kubeinit_spec=okd-libvirt-3-1-1 \
    -i ./kubeinit/inventory.yml \
    ./kubeinit/playbook.yml
```

After provisioning any of the scenarios, you should have your environment ready to go.
To connect to the nodes from the hypervisor use the IP addresses from the inventory files.

## Running the deployment command from a container

The whole process is explained in the [HowTo's](https://www.anstack.com/blog/2020/09/11/Deploying-KubeInit-from-a-container.html).
The following commands build a container image with the project inside of it, and then
launches the container executing the ansible-playbook command with all the
standard ansible-playbook parameters.

Kubeinit is built and installed when deploying from a container as those steps
are included in the Dockerfile, there is no need to build and install
the collection locally if its used through a container.

Note: When running the deployment from a container,
`nyctea` can not be 127.0.0.1, it needs to be
the hypervisor's IP address. Also when running the
deployment as a user different than root, the
keys needs to be also updated.

### Running from the GIT repository

**Note:** Won't work with ARM.

```
git clone https://github.com/Kubeinit/kubeinit.git
cd kubeinit
podman build -t kubeinit/kubeinit .

podman run --rm -it \
    -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:z \
    -v ~/.ssh/id_rsa.pub:/root/.ssh/id_rsa.pub:z \
    -v ~/.ssh/config:/root/.ssh/config:z \
    kubeinit/kubeinit \
        -v --user root \
        -e kubeinit_spec=okd-libvirt-3-1-1 \
        -i ./kubeinit/inventory.yml \
        ./kubeinit/playbook.yml
```

### Running from a release

```
Install [jq](https://stedolan.github.io/jq/)

# Get latest release tag name
TAG=$(curl --silent "https://api.github.com/repos/kubeinit/kubeinit/releases/latest" | jq -r .tag_name)
podman run --rm -it \
    -v ~/.ssh/id_rsa:/root/.ssh/id_rsa:z \
    -v ~/.ssh/id_rsa.pub:/root/.ssh/id_rsa.pub:z \
    -v ~/.ssh/config:/root/.ssh/config:z \
    quay.io/kubeinit/kubeinit:$TAG \
        -v --user root \
        -e kubeinit_spec=okd-libvirt-3-1-1 \
        -i ./kubeinit/inventory.yml \
        ./kubeinit/playbook.yml
```

# HowTo's and presentations

* [The easiest and fastest way to deploy an OKD 4.5 cluster in a Libvirt/KVM Host](https://www.anstack.com/blog/2020/07/31/the-fastest-and-simplest-way-to-deploy-okd-openshift-4-5.html).
* [KubeInit external access for OpenShift/OKD deployments with Libvirt](https://www.anstack.com/blog/2020/08/25/KubeInit-External-access-for-OpenShift-OKD-deployments-with-Libvirt.html).
* [Deploying KubeInit from a container](https://www.anstack.com/blog/2020/09/11/Deploying-KubeInit-from-a-container.html).
* [KubeInit: Bringing good practices from the OpenStack ecosystem to improve the way OKD/OpenShift deploys](https://www.twitch.tv/videos/750577055), [slides](https://speakerdeck.com/redhatopenshift/openshift-deploys).
* [Persistent Volumes And Claims In KubeInit](https://www.anstack.com/blog/2020/09/28/Persistent-volumes-and-claims-in-KubeInit.html)
* [Deploying Multiple KubeInit Clusters In The Same Hypervisor](https://www.anstack.com/blog/2020/10/04/Multiple-KubeInit-clusters-in-the-same-hypervisor.html)
* [KubeInit 4-In-1 - Deploying Multiple Kubernetes Distributions (K8S, OKD, RKE, And CDK) With The Same Platform](https://www.anstack.com/blog/2020/10/19/KubeInit-4-in-1-Deploying-multiple-Kubernetes-distributions-K8S-OKD-RKE-and-CDK-with-the-same-platform.html)

# Supporters

<p style="text-align: center" align="center">
    <a href="https://docs.kubeinit.org/supporters.html#docker"><img width="20%" height="20%" src="https://raw.githubusercontent.com/kubeinit/kubeinit/main/docs/src/static/supporters/docker.svg?sanitize=true" alt="Docker"/></a>
    <a href="https://docs.kubeinit.org/supporters.html#google-cloud-platform"><img width="20%" height="20%" src="https://raw.githubusercontent.com/kubeinit/kubeinit/main/docs/src/static/supporters/gcp.svg?sanitize=true" alt="Google Cloud Platform"/></a>
<!--
    <a href="https://docs.kubeinit.org/supporters.html#red-hat"><img width="20%" height="20%" src="https://raw.githubusercontent.com/kubeinit/kubeinit/main/docs/src/static/supporters/backblaze.svg?sanitize=true" alt="Backblaze"/></a>
    <a href="https://docs.kubeinit.org/supporters.html#red-hat"><img width="20%" height="20%" src="https://raw.githubusercontent.com/kubeinit/kubeinit/main/docs/src/static/supporters/rht.svg?sanitize=true" alt="Red Hat"/></a>
    <a href="https://docs.kubeinit.org/supporters.html#ibm"><img width="20%" height="20%" src="https://raw.githubusercontent.com/kubeinit/kubeinit/main/docs/src/static/supporters/ibm.svg?sanitize=true" alt="IBM"/></a>
-->
</p>
