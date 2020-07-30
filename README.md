<p style="text-align: center" align="center">
    <a href="https://www.kubeinit.com"><img src="https://raw.githubusercontent.com/ccamacho/kubeinit/master/images/logo.svg?sanitize=true" alt="The KUBErnetes INITiator"/></a>
</p>

**The KUBErnetes INITiator**

<p style="text-align: center" align="center">
    <a href="https://www.python.org"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-python.svg?sanitize=true"/> </a>
    <a href="https://www.ansible.com"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-ansible.svg?sanitize=true"/> </a>
    <a href="https://www.kubeinit.com"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/made-with-love.svg?sanitize=true"/> </a>
    <a href="https://www.kubeinit.com"><img height="30px" src="https://raw.githubusercontent.com/pystol/pystol-docs/master/assets/badges/cloud-native.svg?sanitize=true"/> </a>
</p>

## Abstract

KubeInit provides Ansible playbooks and roles for the deployment and configuration of multiple Kubernetes distributions.

## How to run KubeInit

### Requirements

* A server with enough RAM and disk space (120GB in RAM and 300GB in disk).
* A hypervisor with Centos 8.
* We assume that the hypervisor node is called nyctea (defined in the inventory).
* Have root access with certificates.

```bash
ssh root@nyctea
ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -P ""
curl -sS https://github.com/<your_github_username>.keys >> ~/.ssh/authorized_keys
exit
```

### Escenarios

#### Deploy an OKD 4.5 with 3 master nodes and 4 worker nodes.

```bash
git clone https://github.com/ccamacho/kubeinit.git
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

## License

KubeInit is open source software
licensed under the [Apache license](LICENSE).
