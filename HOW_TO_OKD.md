# How to run this role

To deploy the demo server:

Install Centos 8 and then login the first time,
for example:

**We assume the hypervisor is called nyctea as it is defined in the inventory**

```bash
ssh root@nyctea
ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -P ""
curl -sS https://github.com/ccamacho.keys >> ~/.ssh/authorized_keys
exit
```

**Make sure you have enough space in the disk and RAM**

## OK deployment

* Provision the environment packages using libvirt:

```bash
ansible-playbook \
    --user root \
    -v -i ./hosts/okd/inventory \
    --become \
    --become-user root \
    ./playbooks/okd.yml
```

After provisioning the environment, you should have your environment ready to go.
