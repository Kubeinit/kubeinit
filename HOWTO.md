# How to run this role

To deploy the demo server:

Install Centos 7 and then login the first time,
for example:

**We assume the hypervisor has the IP 192.168.1.20**

```bash
ssh root@192.168.1.20
ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -P ""
curl -sS https://github.com/ccamacho.keys >> ~/.ssh/authorized_keys
exit
```

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
sleep 60
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

In this point you should be able to connect to the cluster nodes.

To connect to the cluster nodes you can use the injected root password from the
[guests definition](https://github.com/pystol/pystol-ansible/blob/master/roles/provision/libvirt/defaults/main.yml#L31)
directly with SSH, based on the
[nodes IPs](https://github.com/pystol/pystol-ansible/blob/master/hosts/demo-noha/inventory).

Another way to connect is using virsh connect from the Hypervisor

```bash
[root@vega ~]# virsh list --all
 Id    Name                           State
----------------------------------------------------
 13    kubernetes-master-01           running
 14    kubernetes-worker-01           running
 15    kubernetes-worker-02           running
 16    kubernetes-worker-03           running

[root@vega ~]# virsh console kubernetes-master-01
Connected to domain kubernetes-master-01
kubernetes-master-01 login:
```

Execute (from the master node, kubernetes-master-01.dev.pystol.org):

```bash
kubectl get nodes
```
Then get the output as:

```
NAME                                  STATUS   ROLES    AGE    VERSION
kubernetes-master-01.dev.pystol.org   Ready    master   2m7s   v1.16.3
```

Now, we proceed to install the worker nodes.

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

* Install kubernetes base apps [dashboard,] (master nodes):

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
## Enabling the K8s dashboard

Connect to the master node (kubernetes-master-01) and execute:

```bash
$ cat <<'EOF' | kubectl apply -f -
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kube-system
EOF
```

To make the dashboard accessible via a node-port
change the type in the kubernetes-dashboard service.
Change type: ClusterIP to type: NodePort with the following one-liner.

```bash
kubectl patch svc kubernetes-dashboard -n kubernetes-dashboard --type='json' -p '[{"op":"replace","path":"/spec/type","value":"NodePort"}]'
```

The port that we will use to forward the traffic will be

```bash
kubectl get service -n kubernetes-dashboard kubernetes-dashboard -o json | grep nodePort | sed 's/[^0-9]*//g'
```

**These changes are NOT permanent** On each hypervisor reboot
you need to re-execute them. If you want to make them permanent
uncomment the --permanent parameter.

Execute in the hypervisor (vega):

```bash
dash_port=$(kubectl get service -n kubernetes-dashboard kubernetes-dashboard -o json | grep nodePort | sed 's/[^0-9]*//g')
#Forward vega incoming traffic to the k8s master node
firewall-cmd --zone=public --add-masquerade #--permanent
firewall-cmd --zone=public --direct --add-rule ipv4 filter FORWARD 0 -d 0.0.0.0/0 -j ACCEPT #--permanent

# The dashboard port forwarding
firewall-cmd --zone=public --add-port=<dash_port_value>/tcp #--permanent
firewall-cmd --zone=public --add-forward-port=port=8001:proto=tcp:toport=<dash_port_value>:toaddr=10.0.0.1 #--permanent

# The Pystol UI port forwarding
firewall-cmd --zone=public --add-port=3000/tcp #--permanent
firewall-cmd --zone=public --add-forward-port=port=3000:proto=tcp:toport=3000:toaddr=10.0.0.1 #--permanent
```

Test the endpoints:

```bash
curl http://vega:8001/api/v1/namespaces/kubernetes-dashboard/services/kubernetes-dashboard/
curl http://vega:8001/api/v1/namespaces/kubernetes-dashboard/services/
```

Now open from any host that can reach the hypervisor:

```bash
https://vega:<dash_port_value>/
```

Use the token from the master node to login in the dashboard:

```bash
kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep admin-user | awk '{print $1}') | grep ^token: | sed 's/token:[ ]*//'
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
