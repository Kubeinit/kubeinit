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
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=docs_build"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/docs_build/badge.svg?event=push"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=molecule"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/molecule/badge.svg?event=push"/> </a>
    <a href="https://github.com/Kubeinit/kubeinit/actions?workflow=galaxy_publish"><img height="20px" src="https://github.com/Kubeinit/kubeinit/workflows/galaxy_publish/badge.svg?event=push"/> </a>
    <a href="https://opensource.org/licenses/Apache-2.0"><img height="20px" src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"/> </a>
</p>

# Abstract

KubeInit provides Ansible playbooks and roles for the deployment and configuration of multiple Kubernetes distributions.
The main goal of KubeInit is to have a fully automated way to deploy in a single command a curated list of
prescribed architectures.

# Documentation

KubeInit's documentation is hosted in [this same repository](https://kubeinit.github.io/kubeinit/).
The documentation is rendered using Sphinx and uploaded to GitHub pages using a GitHub action.

# KubeInit supported scenarios

  <table>
    <tbody>
      <tr>
        <td rowspan="2" style="font-weight: bold;">K8s distro</td>
        <td colspan="2" style="font-weight: bold;text-align:center;">Driver</td>
      </tr>
      <tr>
        <td style="font-weight: bold;text-align:center;">Libvirt host</td>
        <td style="font-weight: bold;text-align:center;">Baremetal</td>
      </tr>
      <tr>
        <td>Origin</td>
        <td>CentOS/Fedora<br/>Debian/Ubuntu</td>
        <td>WIP</td>
      </tr>
      <tr>
        <td>Kubernetes</td>
        <td>WIP</td>
        <td>WIP</td>
      </tr>
    </tbody>
  </table>

# Requirements

* A fresh deployed server with enough RAM and disk space (120GB in RAM and 300GB in disk) and CentOS 8 (it should work also in Fedora/Debian/Ubuntu hosts).
* We assume that the hypervisor node is called nyctea (defined in the inventory).
* Have root access with certificates.
* Adjust the inventory file to suit your needs i.e. [the worker nodes](https://github.com/Kubeinit/kubeinit/blob/master/kubeinit/hosts/okd/inventory#L66)
 you will need in your cluster.

# How to run

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

# HowTo's

* [The easiest and fastest way to deploy an OKD 4.5 cluster in a Libvirt/KVM Host](https://www.anstack.com/blog/2020/07/31/the-fastest-and-simplest-way-to-deploy-okd-openshift-4-5.html)
* [KubeInit external access for OpenShift/OKD deployments with Libvirt](https://www.anstack.com/blog/2020/08/25/KubeInit-External-access-for-OpenShift-OKD-deployments-with-Libvirt.html)
